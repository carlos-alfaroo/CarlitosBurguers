from flask import Flask, render_template, request, redirect, url_for
from collections import deque

app = Flask(__name__)

# --- Arrays ---
MAX_ORDENES = 10
ordenes_array = [None]*MAX_ORDENES
indice = 0

# --- Lista ligada para historial de pedidos ---
class Nodo:
    def __init__(self, pedido):
        self.pedido = pedido
        self.siguiente = None

class ListaLigada:
    def __init__(self):
        self.head = None

    def insertar(self, pedido):
        nodo = Nodo(pedido)
        nodo.siguiente = self.head
        self.head = nodo

historial_pedidos = ListaLigada()

# --- Pila y cola ---
pila_urgentes = []
cola_reservas = deque(maxlen=5)

# --- Crear pedido ---
def crear_pedido(nombre_cliente, mesa, plato):
    return {
        "cliente": nombre_cliente,
        "mesa": mesa,
        "plato": plato
    }

# --- Registrar pedido ---
def registrar_pedido(nombre_cliente, mesa, plato, urgente=False):
    global indice
    pedido = crear_pedido(nombre_cliente, mesa, plato)
    ordenes_array[indice] = pedido
    indice = (indice + 1) % MAX_ORDENES
    historial_pedidos.insertar(pedido)
    if urgente:
        pila_urgentes.append(pedido)
    return pedido

# --- Agregar reserva ---
def agregar_reserva(nombre_cliente, mesa):
    reserva = {"cliente": nombre_cliente, "mesa": mesa}
    cola_reservas.append(reserva)
    return reserva

# --- Editar pedido ---
@app.route('/editar/<int:pos>', methods=['GET', 'POST'])
def editar_pedido(pos):
    pedido = ordenes_array[pos]
    if not pedido:
        return redirect(url_for('index'))

    if request.method == 'POST':
        pedido['cliente'] = request.form.get('nombre')
        pedido['mesa'] = request.form.get('mesa')
        pedido['plato'] = request.form.get('plato')
        return redirect(url_for('index'))

    return render_template('editar.html', pedido=pedido, pos=pos)

# --- Eliminar pedido ---
@app.route('/eliminar/<int:pos>')
def eliminar_pedido(pos):
    ordenes_array[pos] = None
    return redirect(url_for('index'))
  
# --- Editar reserva ---
@app.route('/editar_reserva/<int:pos>', methods=['GET', 'POST'])
def editar_reserva(pos):
    if pos < 0 or pos >= len(cola_reservas):
        return redirect(url_for('index'))
    
    reserva = cola_reservas[pos]

    if request.method == 'POST':
        reserva['cliente'] = request.form.get('nombre')
        reserva['mesa'] = request.form.get('mesa')
        return redirect(url_for('index'))

    return render_template('editar.html', pedido=reserva, pos=pos, tipo='reserva')

# --- Eliminar reserva ---
@app.route('/eliminar_reserva/<int:pos>')
def eliminar_reserva(pos):
    if 0 <= pos < len(cola_reservas):
        del cola_reservas[pos]
    return redirect(url_for('index'))
  
# --- Editar pedido urgente (pila) ---
@app.route('/editar_urgente/<int:pos>', methods=['GET', 'POST'])
def editar_pedido_urgente(pos):
    if pos < 0 or pos >= len(pila_urgentes):
        return redirect(url_for('index'))
    
    pedido = pila_urgentes[pos]

    if request.method == 'POST':
        pedido['cliente'] = request.form.get('nombre')
        pedido['mesa'] = request.form.get('mesa')
        pedido['plato'] = request.form.get('plato')
        return redirect(url_for('index'))

    return render_template('editar.html', pedido=pedido, pos=pos)

# --- Eliminar último pedido (array) ---
@app.route('/eliminar_array')
def eliminar_array():
    global indice
    # Buscar último pedido válido
    for i in range(MAX_ORDENES-1, -1, -1):
        if ordenes_array[i] is not None:
            ordenes_array[i] = None
            break
    return redirect(url_for('index'))

# --- Eliminar tope de pila (urgentes) ---
@app.route('/eliminar_pila')
def eliminar_pila():
    if pila_urgentes:
        pila_urgentes.pop()
    return redirect(url_for('index'))

# --- Eliminar primer elemento de la cola (reservas) ---
@app.route('/eliminar_cola')
def eliminar_cola():
    if cola_reservas:
        cola_reservas.popleft()
    return redirect(url_for('index'))
# --- Ruta principal ---
@app.route('/', methods=['GET', 'POST'])
def index():
    global indice
    if request.method == 'POST':
        tipo = request.form.get("tipo")
        nombre = request.form.get("nombre")
        mesa = request.form.get("mesa")
        plato = request.form.get("plato")
        urgente = request.form.get("urgente") == "on"

        if tipo == "pedido":
            registrar_pedido(nombre, mesa, plato, urgente)
        elif tipo == "reserva":
            agregar_reserva(nombre, mesa)

        return redirect(url_for('index'))

    return render_template('index.html',
                           ordenes_array=ordenes_array,
                           pila_urgentes=pila_urgentes,
                           cola_reservas=list(cola_reservas))


# --- Bloque principal debe ir fuera de cualquier función ---
if __name__ == '__main__':
    app.run(debug=True, port=5001)