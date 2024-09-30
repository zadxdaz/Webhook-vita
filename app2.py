import sqlite3
from objetos2 import *
from flask import Flask, g , render_template , request , redirect , url_for

app = Flask(__name__)
KEY = "EAA0yrfyTgOgBO4hDOxhHwWcGUq86GU0hJmzTPR0I07I0klGkFykjYXVjcw2yOwt5ja0QQ3WVmtyPmYsbd1ZCMaruPvjM4QNYhPtwx1aMnbMcJ9JVZBnauxnRVXA8DZCyB0nIrEMUOE3kZCns43JNxMuTZBIfgyzXxLlxCBl3WQjX29V7ZBKUO8qxx9P3mF1Bcs6wZDZD"
PHONE_NUMBER_ID ="3714897545494760"
WEBHOOK_VERIFY_TOKEN="ASLDNKFUIOQWHBDFA213fa"
DATABASE = 'vita.db'
bot = Bot()
bot.ACCESS_TOKEN = KEY


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Permite acceder a los datos por nombre de columna
    return conn


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/webhook', methods =['POST'])
def webhook():
    data = request.get_json()
    bot.procesar_mensaje(data)
    return "Ok" ,200

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    # Obtiene los parámetros de la solicitud GET
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    # Verifica que el modo y el token son correctos
    if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN:
        # Responde con el challenge token para verificar el webhook
        return challenge, 200
    else:
        # Responde con 403 si el token no coincide
        return "Forbidden", 403

@app.route('/iniciar_conversacion/<int:id>', methods=['POST'])
def iniciar_conversacion(id):
    # Obtener el cliente por su ID
    cliente = Cliente.get_by_id(id)

    if cliente:
        # Enviar un mensaje de saludo con opciones al cliente
        bot.enviar_saludo(cliente)

    return redirect(url_for('index'))

# Ruta para listar todos los clientes
@app.route('/')
def index():
    clientes = Cliente.get_all()  # Obtener todos los clientes a través de la clase Cliente
    return render_template('index.html', clientes=clientes)
# Ruta para crear un nuevo cliente (GET para mostrar el formulario, POST para procesar la data)
@app.route('/nuevo_cliente', methods=['GET', 'POST'])
def nuevo_cliente():
    if request.method == 'POST':
        nombre = request.form['nombre_completo']
        celular = request.form['celular']
        direccion = request.form['direccion']

        cliente = Cliente(nombre_completo=nombre, celular=celular, direccion=direccion)
        cliente.save()  # Usar el método save() para guardar el cliente en la base de datos
        return redirect(url_for('index'))
    return render_template('nuevo_cliente.html')

# Ruta para editar un cliente
@app.route('/editar_cliente/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    cliente = Cliente.get_by_id(id)  # Obtener el cliente por su ID

    if request.method == 'POST':
        nombre = request.form['nombre_completo']
        celular = request.form['celular']
        direccion = request.form['direccion']

        cliente.nombre_completo = nombre
        cliente.celular = celular
        cliente.direccion = direccion
        cliente.save()  # Actualizar el cliente usando el método save()
        return redirect(url_for('index'))

    return render_template('editar_cliente.html', cliente=cliente)

# Ruta para eliminar un cliente
@app.route('/eliminar_cliente/<int:id>', methods=['POST'])
def eliminar_cliente(id):
    cliente = Cliente.get_by_id(id)
    if cliente:
        cliente.delete()  # Eliminar el cliente usando el método delete()
    return redirect(url_for('index'))

# Ruta para listar todos los productos
@app.route('/productos')
def productos():
    productos = Producto.get_all()
    return render_template('productos.html', productos=productos)

# Ruta para crear un nuevo producto (GET para mostrar el formulario, POST para procesar la data)
@app.route('/nuevo_producto', methods=['GET', 'POST'])
def nuevo_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']

        producto = Producto(nombre=nombre, descripcion=descripcion, precio=precio)
        producto.save()
        return redirect(url_for('productos'))
    return render_template('nuevo_producto.html')

# Ruta para editar un producto
@app.route('/editar_producto/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    producto = Producto.get_by_id(id)

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']

        producto.nombre = nombre
        producto.descripcion = descripcion
        producto.precio = precio
        producto.save()
        return redirect(url_for('productos'))

    return render_template('editar_producto.html', producto=producto)

# Ruta para eliminar un producto
@app.route('/eliminar_producto/<int:id>', methods=['POST'])
def eliminar_producto(id):
    producto = Producto.get_by_id(id)
    if producto:
        producto.delete()
    return redirect(url_for('productos'))

# Ruta para listar todos los pedidos
@app.route('/pedidos')
def pedidos():
    pedidos = Pedido.get_vista()
    return render_template('pedidos.html', pedidos=pedidos)

# Ruta para crear un nuevo pedido (GET para mostrar el formulario, POST para procesar la data)
@app.route('/nuevo_pedido', methods=['GET', 'POST'])
def nuevo_pedido():
    clientes = Cliente.get_all()
    productos = Producto.get_all()

    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        producto_id = request.form['producto_id']
        cantidad = request.form['cantidad']
        estado = request.form['estado']

        pedido = Pedido(cliente_id=cliente_id, producto_id=producto_id, cantidad=cantidad, estado=estado)
        pedido.save()
        return redirect(url_for('pedidos'))
    return render_template('nuevo_pedido.html', clientes=clientes, productos=productos)

# Ruta para editar un pedido
@app.route('/editar_pedido/<int:id>', methods=['GET', 'POST'])
def editar_pedido(id):
    pedido = Pedido.get_by_id(id)
    clientes = Cliente.get_all()
    productos = Producto.get_all()

    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        producto_id = request.form['producto_id']
        cantidad = request.form['cantidad']
        estado = request.form['estado']

        pedido.cliente_id = cliente_id
        pedido.producto_id = producto_id
        pedido.cantidad = cantidad
        pedido.estado = estado
        pedido.save()
        return redirect(url_for('pedidos'))

    return render_template('editar_pedido.html', pedido=pedido, clientes=clientes, productos=productos)

# Ruta para eliminar un pedido
@app.route('/eliminar_pedido/<int:id>', methods=['POST'])
def eliminar_pedido(id):
    pedido = Pedido.get_by_id(id)
    if pedido:
        pedido.delete()
    return redirect(url_for('pedidos'))


if __name__ == '__main__':
    app.run(debug=True)