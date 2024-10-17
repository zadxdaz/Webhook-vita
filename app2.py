import os
import sqlite3
from flask import Flask, g, render_template, request, redirect, url_for, abort , jsonify, flash
from flask_wtf.csrf import CSRFProtect 
from flask_wtf import FlaskForm
from objetos2 import *
import functools
from datetime import datetime


# Load sensitive data from environment variables
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("WHATSAPP_API_KEY")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN")
DATABASE = os.getenv("DATABASE", "vita.db")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
csrf = CSRFProtect(app)

bot = Bot(KEY,PHONE_NUMBER_ID)

# Database connection
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

class EmptyForm(FlaskForm):
    pass

@app.teardown_appcontext
def close_db_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Error handler
def handle_db_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return abort(500, description="Internal Server Error")
    return wrapper

# Routes with improvements

@app.route('/webhook', methods=['POST'])
@csrf.exempt
def webhook():
    data = request.get_json()
    bot.procesar_mensaje(data)
    return "Ok", 200

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

@app.route('/iniciar_conversacion/<int:id>', methods=['POST'])
@handle_db_error
def iniciar_conversacion(id):
    cliente = Cliente.get_by_id(id)
    if cliente:
        bot.enviar_saludo(cliente)
    return redirect(url_for('index'), 302)

@app.route('/')
@handle_db_error
def index():
    clientes = Cliente.get_all()
    form = EmptyForm()
    return render_template('index.html', clientes=clientes,  form=form), 200

@app.route('/nuevo_cliente', methods=['GET', 'POST'])
@handle_db_error
def nuevo_cliente():
    form=EmptyForm()
    if request.method == 'POST':
        nombre = request.form['nombre_completo']
        celular = request.form['celular']
        direccion = request.form['direccion']

        cliente = Cliente(nombre_completo=nombre, celular=celular, direccion=direccion)
        cliente.save()
        return redirect(url_for('index'), 302)
    return render_template('nuevo_cliente.html',form=form), 200

@app.route('/editar_cliente/<int:id>', methods=['GET', 'POST'])
@handle_db_error
def editar_cliente(id):
    cliente = Cliente.get_by_id(id)
    if request.method == 'POST':
        nombre = request.form['nombre_completo']
        celular = request.form['celular']
        direccion = request.form['direccion']

        cliente.nombre_completo = nombre
        cliente.celular = celular
        cliente.direccion = direccion
        cliente.save()
        return redirect(url_for('index'), 302)

    return render_template('editar_cliente.html', cliente=cliente), 200

@app.route('/eliminar_cliente/<int:id>', methods=['POST'])
@handle_db_error
def eliminar_cliente(id):
    cliente = Cliente.get_by_id(id)
    if cliente:
        cliente.delete()
    return redirect(url_for('index'), 302)

@app.route('/productos')
@handle_db_error
def productos():
    form=EmptyForm()
    productos = Producto.get_all()
    return render_template('productos.html', productos=productos,form=form), 200

@app.route('/nuevo_producto', methods=['GET', 'POST'])
@handle_db_error
def nuevo_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']

        producto = Producto(nombre=nombre, descripcion=descripcion, precio=precio)
        producto.save()
        return redirect(url_for('productos'), 302)
    return render_template('nuevo_producto.html'), 200

@app.route('/editar_producto/<int:id>', methods=['GET', 'POST'])
@handle_db_error
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
        return redirect(url_for('productos'), 302)

    return render_template('editar_producto.html', producto=producto), 200

@app.route('/eliminar_producto/<int:id>', methods=['POST'])
@handle_db_error
def eliminar_producto(id):
    producto = Producto.get_by_id(id)
    if producto:
        producto.delete()
    return redirect(url_for('productos'), 302)

@app.route('/pedidos')
@handle_db_error
def pedidos():
    form = EmptyForm()
    pedidos = Pedido.get_vista()
    return render_template('pedidos.html', pedidos=pedidos, form=form), 200

@app.route('/nuevo_pedido', methods=['GET', 'POST'])
@handle_db_error
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
        return redirect(url_for('pedidos'), 302)
    return render_template('nuevo_pedido.html', clientes=clientes, productos=productos), 200

@app.route('/editar_pedido/<int:id>', methods=['GET', 'POST'])
@handle_db_error
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
        return redirect(url_for('pedidos'), 302)

    return render_template('editar_pedido.html', pedido=pedido, clientes=clientes, productos=productos), 200

@app.route('/eliminar_pedido/<int:id>', methods=['POST'])
@handle_db_error
def eliminar_pedido(id):
    pedido = Pedido.get_by_id(id)
    if pedido:
        pedido.delete()
    return redirect(url_for('pedidos'), 302)

@app.route('/client_messages/<whatsapp_id>', methods=['GET'])
def client_messages(whatsapp_id):
    conn = Mensaje.get_db_connection()
    form = EmptyForm()
    try:
        # Fetch the client's data based on the whatsapp_id
        client = Cliente.obtener_por_celular(whatsapp_id)
    except sqlite3.Error as e:
        print(f"Error retrieving messages for {whatsapp_id}: {e}")
        messages = []
        has_more = False
        client = None
    finally:
        Mensaje.close_connection(conn)

    return render_template('client_messages.html',  
                           whatsapp_id=whatsapp_id, 
                           client=client,form=form )

@app.route('/api/messages/<whatsapp_id>', methods=['GET'])
@csrf.exempt
def api_client_messages(whatsapp_id):
    # Get the 'page' query parameter to handle pagination, default to 1 if not provided
    page = int(request.args.get('page', 1))
    per_page = 100  # Number of messages to load per page
    offset = (page - 1) * per_page

    conn = Mensaje.get_db_connection()
    try:
        cursor = conn.cursor()
        # Fetch the messages for the specific client
        cursor.execute('''
            SELECT * FROM mensajes 
            WHERE whatsapp_id = ?
            ORDER BY timestamp ASC
            LIMIT ? OFFSET ?
        ''', (whatsapp_id, per_page, offset))
        messages = cursor.fetchall()

        # Check if there are more messages for pagination
        cursor.execute('SELECT COUNT(*) FROM mensajes WHERE whatsapp_id = ?', (whatsapp_id,))
        total_messages = cursor.fetchone()[0]
        has_more = total_messages > offset + per_page
        messages_data = [
            {
                'id': message['id'],
                'message': message['message'],
                'direction': message['direction'],
                'timestamp': message['timestamp']
            } for message in messages
        ]
    except sqlite3.Error as e:
        print(f"Error retrieving messages: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        Mensaje.close_connection(conn)

    # Return messages in JSON format with pagination info
    return jsonify({
        'messages': messages_data,
        'has_more': has_more,
        'page': page
    })

@app.route('/api/send_message/<whatsapp_id>', methods=['POST'])
@csrf.exempt
def send_message(whatsapp_id):
    data = request.get_json()
    message_text = data.get('message')

    # Generate the current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    bot.enviar_mensaje(celular=whatsapp_id,mensaje=message_text)
    # Return the message_id and timestamp in the response
    return jsonify({"status": "Message sent successfully", "timestamp": timestamp}), 200

@app.route('/reset_conversation/<int:id>', methods=['POST'])
def reset_conversation(id):
    # Retrieve the client from the database
    client = Cliente.get_by_id(id)

    if client:
        # Reset estado_conversacion and producto_seleccionado to None
        client.estado_conversacion = None
        client.producto_seleccionado = None
        client.save()

    # Redirect back to the client message screen after resetting
    return redirect(url_for('client_messages', whatsapp_id=client.celular))

@app.route('/client-lists', methods=['GET'])
def view_all_client_lists():
    """Display all client lists."""
    client_lists = ClientesList.get_all()  # Fetch all client lists
    return render_template('client_lists.html', client_lists=client_lists)

@app.route('/client-list/<int:lista_id>', methods=['GET'])
def view_client_list(lista_id):
    """Display a specific client list and its clients."""
    client_list = ClientesList.get_by_id(lista_id)  # Fetch the specific list
    if not client_list:
        flash('Client list not found', 'error')
        return redirect(url_for('view_all_client_lists'))

    clients = client_list.get_clientes()  # Fetch all clients in the list
    all_clients = Cliente.get_all()  # Fetch all available clients to add to the list

    form = EmptyForm()  # Form to protect against CSRF
    return render_template('client_list.html', client_list=client_list, clients=clients, all_clients=all_clients, form=form)

@app.route('/client-list/<int:lista_id>/add-client', methods=['POST'])
def add_client_to_list(lista_id):
    """Add a client to the list."""
    client_list = ClientesList.get_by_id(lista_id)
    form = EmptyForm()
    if form.validate_on_submit():
        cliente_id = request.form.get('cliente_id')
        if cliente_id:
            client_list.add_cliente(cliente_id)
            flash('Client added successfully', 'success')
        else:
            flash('No client selected', 'error')
    return redirect(url_for('view_client_list', lista_id=lista_id))

@app.route('/client-list/<int:lista_id>/remove-client/<int:cliente_id>', methods=['POST'])
def remove_client_from_list(lista_id, cliente_id):
    """Remove a client from the list."""
    client_list = ClientesList.get_by_id(lista_id)
    form = EmptyForm()
    if form.validate_on_submit():
        client_list.remove_cliente(cliente_id)
        flash('Client removed successfully', 'success')
    return redirect(url_for('view_client_list', lista_id=lista_id))

@app.route('/client-list/<int:lista_id>/rename', methods=['POST'])
def rename_client_list(lista_id):
    """Rename the client list."""
    client_list = ClientesList.get_by_id(lista_id)
    form = EmptyForm()
    if form.validate_on_submit():
        new_name = request.form.get('new_name')
        if new_name:
            client_list.rename(new_name)
            flash('Client list renamed successfully', 'success')
        else:
            flash('Name cannot be empty', 'error')
    return redirect(url_for('view_client_list', lista_id=lista_id))

@app.route('/client-list/<int:lista_id>/send-message', methods=['POST'])
def send_message_to_clients(lista_id):
    """Send a message to all clients in the list using the Bot.enviar_saludo method."""
    client_list = ClientesList.get_by_id(lista_id)
    if not client_list:
        flash('Client list not found', 'error')
        return redirect(url_for('view_all_client_lists'))

    clients = client_list.get_clientes()  # Get all clients in the list
    form = EmptyForm()
    
    if form.validate_on_submit(): 
        for client in clients:
            bot.enviar_saludo(client)  # Send a message to each client

        flash(f'Message sent to {len(clients)} clients', 'success')
    else:
        flash('Failed to send messages', 'error')

    return redirect(url_for('view_client_list', lista_id=lista_id))



if __name__ == '__main__':
    app.run(debug=True)
