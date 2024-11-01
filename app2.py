import os
import sqlite3
from flask import Flask, g, render_template, request, redirect, url_for, abort , jsonify, flash
from flask_wtf.csrf import CSRFProtect 
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired, Length
from objects import *
from objects import db
import functools
from datetime import datetime,timedelta
from flask_sqlalchemy import SQLAlchemy


# Load sensitive data from environment variables
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("WHATSAPP_API_KEY")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN")
DATABASE = os.getenv("DATABASE", "vita.db")
ENVIRONMENT = os.getenv("ENVIROMENT")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
csrf = CSRFProtect(app)

bot = Bot(KEY,PHONE_NUMBER_ID)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE

class EmptyForm(FlaskForm):
    pass

class ClientListForm(FlaskForm):
    nombre = StringField('List Name', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Create List')


if ENVIRONMENT == 'Debug':
    # Set up SSH tunnel for remote MySQL database access
    print(2)
    tunnel = sshtunnel.SSHTunnelForwarder(
        ('ssh.pythonanywhere.com'),
        ssh_username='zadxdaz',
        ssh_password='Ickkdbbi2p2.',
        remote_bind_address=('zadxdaz.mysql.pythonanywhere-services.com', 3306)
    )
    tunnel.start()

    # Construct the database URI with the tunnel's local bind port
    app.config["SQLALCHEMY_DATABASE_URI"] = f'mysql://zadxdaz:sqlvitamovil@127.0.0.1:{tunnel.local_bind_port}/zadxdaz$test'
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE



init_app(app)
    
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

@app.route('/', methods=['GET'])
@handle_db_error
def index():
    search_query = request.args.get('search', '')  # Get the search query from the URL
    page = int(request.args.get('page', 1))  # Get the current page, default to 1
    per_page = 10  # Set the number of clients to display per page

    # Query to fetch clients, optionally filter by name
    if search_query:
        clientes = Cliente.search_by_name(search_query)
    else:
        clientes = Cliente.get_all()

    # Paginate the results
    total_clients = len(clientes)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_clients = clientes[start:end]

    # Fetch balance for each client
    client_data = []
    for client in paginated_clients:
        balance = client.get_balance()
        client_data.append({
            'client': client,
            'balance': balance
        })

    form = EmptyForm()

    return render_template(
        'index.html', 
        clients=client_data, 
        search_query=search_query, 
        page=page, 
        per_page=per_page, 
        total_clients=total_clients,
        form=form
    )

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
    form = EmptyForm()
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        

        producto = Producto(nombre=nombre, descripcion=descripcion, precio=precio)
        producto.save()
        return redirect(url_for('productos'), 302)
    return render_template('nuevo_producto.html',form=form), 200

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

@app.route('/pedidos', methods=['GET', 'POST'])
@handle_db_error
def pedidos():
    form = EmptyForm()
    state_filter = request.args.get('state', 'pendiente')  # Default to 'pendiente'
    search_query = request.args.get('search', '').strip()  # Optional search query
    
    # Fetch pedidos based on the filters
    pedidos = Pedido.get_vista(state=state_filter, search=search_query)
    
    # Get unique states for dropdown filter options
    all_states = Pedido.get_unique_states()
    
    return render_template('pedidos.html', pedidos=pedidos, form=form, 
                           state_filter=state_filter, search_query=search_query,
                           all_states=all_states), 200

@app.route('/nuevo_pedido', methods=['GET', 'POST'])
@handle_db_error
def nuevo_pedido():
    form = EmptyForm()
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
    return render_template('nuevo_pedido.html', clientes=clientes, productos=productos,form=form), 200

@app.route('/editar_pedido/<int:id>', methods=['GET', 'POST'])
@handle_db_error
def editar_pedido(id):
    pedido = Pedido.get_by_id(id)
    clientes = Cliente.get_all()
    productos = Producto.get_all()
    form = EmptyForm()

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

    return render_template('editar_pedido.html', pedido=pedido, clientes=clientes, productos=productos,form = form), 200

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

@app.route('/nuevo_lista', methods=['GET', 'POST'])
@handle_db_error
def nuevo_lista():
    form = ClientListForm()
    if form.validate_on_submit():
        # Create new client list using the submitted form data
        client_list = ClientesList(nombre=form.nombre.data)
        client_list.save()
        flash('New client list created successfully!', 'success')
        return redirect(url_for('view_all_client_lists'))
    
    return render_template('nuevo_lista.html', form=form), 200

@app.route('/api/cliente/<int:client_id>/balance', methods=['GET'])
def get_client_balance(client_id):
    client = Cliente.get_by_id(client_id)
    if not client:
        return jsonify({'error': 'Client not found'}), 404

    balance = client.get_balance()
    return jsonify({'client_id': client_id, 'balance': balance}), 200

@app.route('/accounting', methods=['GET', 'POST'])
@handle_db_error
def accounting():
    # Handle adding a new transaction via POST request
    if request.method == 'POST':
        client_id = request.form.get('client_id')
        amount = float(request.form.get('amount'))
        description = request.form.get('description')
        transaction_type = request.form.get('transaction_type')  # 'debt' or 'payment'

        # Create a transaction (positive amount for payment, negative for debt)
        if transaction_type == 'debt':
            amount = -abs(amount)  # Convert to negative for debts
        else:
            amount = abs(amount)  # Ensure it's positive for payments

        transaction = Transaction(client_id=client_id, amount=amount, description=description)
        transaction.save()

        flash('Transaction added successfully!', 'success')
        return redirect(url_for('accounting'))

    # Fetch all transactions
    transactions = Transaction.get_all()

    # Fetch debts older than one month
    one_month_ago = datetime.now() - timedelta(days=30)
    old_debts = Transaction.get_debts_older_than(one_month_ago)

    # Fetch all clients to populate the form
    clients = Cliente.get_all()

    return render_template('accounting.html', transactions=transactions, old_debts=old_debts, clients=clients)

@app.route('/hoja-de-ruta/nueva', methods=['POST'])
@handle_db_error
def create_hoja_de_ruta():
    # Get selected pedidos (orders) from the form
    pedidos_ids = request.form.getlist('pedido_id')
    
    if not pedidos_ids:
        flash('No orders selected', 'error')
        return redirect(url_for('pedidos'))

    # Create a new Hoja de Ruta (Delivery Route)
    
    hoja_de_ruta = HojaDeRuta()
    db.session.add(hoja_de_ruta)
    db.session.commit()
      # Save to DB to get the new hoja_de_ruta.id

    # Add the selected pedidos to the Hoja de Ruta with the status 'on delivery'
    for index, pedido_id in enumerate(pedidos_ids):
        hoja_de_ruta_pedido = HojaDeRutaPedido(
            hoja_de_ruta_id=hoja_de_ruta.id,
            pedido_id=pedido_id,
            posicion=index + 1,  # Position in the list
            estado='on delivery'
        )
        hoja_de_ruta_pedido.save()

        # Update the state of the pedido to 'on delivery'
        pedido = Pedido.get_by_id(pedido_id)
        pedido.estado = 'on delivery'
        pedido.save()
    flash('Hoja de Ruta created successfully!', 'success')
    return redirect(url_for('view_hoja_de_ruta', hoja_id=hoja_de_ruta.id))

@app.route('/hoja-de-ruta/<int:hoja_id>', methods=['GET', 'POST'])
@handle_db_error
def view_hoja_de_ruta(hoja_id):
    hoja_de_ruta = HojaDeRuta.get_by_id(hoja_id)
    form=EmptyForm()
    if request.method == 'POST':
        # Handle updating positions or marking orders as delivered
        pedidos_posiciones = request.form.getlist('pedido_posicion')
        entregado_pedido_id = request.form.get('entregado_pedido_id')

        # Update positions of the pedidos in the hoja de ruta
        if pedidos_posiciones:
            for index, pedido_id in enumerate(pedidos_posiciones):
                hoja_de_ruta_pedido = HojaDeRutaPedido.get_by_pedido_id_and_hoja_id(pedido_id, hoja_id)
                hoja_de_ruta_pedido.posicion = index + 1
                hoja_de_ruta_pedido.save()

        # Mark a pedido as delivered and create debt for the client
        if entregado_pedido_id:
            hoja_de_ruta_pedido = HojaDeRutaPedido.get_by_pedido_id_and_hoja_id(entregado_pedido_id, hoja_id)
            hoja_de_ruta_pedido.estado = 'delivered'
            hoja_de_ruta_pedido.save()

            # Update the pedido state
            pedido = Pedido.get_by_id(entregado_pedido_id)
            pedido.estado = 'delivered'
            pedido.save()

            # Create a debt for the client
            debt = Transaction(
                client_id=pedido.cliente_id,
                amount=-pedido.total,  # Negative amount to indicate debt
                description=f"Delivery of order {pedido.id}"
            )
            debt.save()

            flash('Pedido marked as delivered and debt created!', 'success')

        return redirect(url_for('view_hoja_de_ruta', hoja_id=hoja_id))

    # Fetch all pedidos in the hoja de ruta
    pedidos = HojaDeRutaPedido.get_detalle_by_hoja_id(hoja_id)

    return render_template('hoja_de_ruta.html', hoja_de_ruta=hoja_de_ruta, pedidos=pedidos,form=form)

@app.route('/hoja-de-ruta/<int:hoja_id>/pedido/<int:pedido_id>/<string:estado>', methods=['POST'])
def mark_as_delivered(hoja_id, pedido_id,estado):
    form = EmptyForm()
    if form.validate_on_submit():
        hoja_pedido = HojaDeRutaPedido.get_by_pedido_id_and_hoja_id(pedido_id, hoja_id)
        if hoja_pedido:
            if estado == 'entregado':
                hoja_pedido.estado = 'entregado'
                hoja_pedido.save()
                # Update the Pedido state to 'delivered'
                pedido = Pedido.get_by_id(pedido_id)
                pedido.estado='delivered'
                deuda = Transaction(amount=-(pedido.total),client_id=pedido.cliente_id,date=datetime.now())
                flash('Pedido marked as delivered!', 'success')
            elif estado == 'cancelado':
                hoja_pedido.estado = 'canceled'
                hoja_pedido.save()
                pedido = Pedido.get_by_id(pedido_id)
                pedido.estado='cancelado'
                flash('Pedido has been canceled.', 'success')
            
            db.session.commit()

            
        else:
            flash('Pedido not found in the Hoja de Ruta.', 'error')
    
    return redirect(url_for('view_hoja_de_ruta', hoja_id=hoja_id))

@app.route('/hojas-de-ruta', methods=['GET'])
@handle_db_error
def view_all_hojas_de_ruta():
    """Display a list of all Hojas de Ruta."""
    hojas = HojaDeRuta.get_all()  # Assuming get_all() retrieves all Hojas de Ruta
    return render_template('hojas_de_ruta.html', hojas=hojas)

@app.route('/hoja-de-ruta/<int:hoja_id>/pedido/<int:pedido_id>/cancelar', methods=['POST'])
@handle_db_error
def mark_as_canceled(hoja_id, pedido_id):
    form = EmptyForm()
    if form.validate_on_submit():
        hoja_pedido = HojaDeRutaPedido.get_by_pedido_id_and_hoja_id(pedido_id, hoja_id)
        if hoja_pedido:
            # Update the HojaDeRutaPedido and Pedido statuses to 'canceled'
            hoja_pedido.estado = 'canceled'
            hoja_pedido.save()

            pedido = Pedido.get_by_id(pedido_id)
            pedido.update_estado('canceled')

            # Optional: Add logic for reversing or logging the canceled order
            flash('Pedido has been canceled.', 'success')
        else:
            flash('Pedido not found in the Hoja de Ruta.', 'error')
    
    return redirect(url_for('view_hoja_de_ruta', hoja_id=hoja_id))



# Run the app with SSH tunnel
if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        # Ensure SSH tunnel is closed when the app shuts down
        if 'tunnel' in locals() and tunnel.is_active:
            tunnel.close()