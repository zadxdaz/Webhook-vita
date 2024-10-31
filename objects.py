from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime
from dotenv import load_dotenv
import sshtunnel
import os
import requests
import time

load_dotenv()
DATABASE_URI = os.getenv('DATABASE', 'sqlite:///vita.db')
ENVIROMENT = os.getenv("ENVIROMENT")
db = SQLAlchemy()

def init_app(app):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

class Cliente(db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_completo = db.Column(db.String(255), nullable=False)
    celular = db.Column(db.String(20), nullable=False, unique=True)
    direccion = db.Column(db.String(255), nullable=False)
    estado_conversacion = db.Column(db.String(50), nullable=True)
    producto_seleccionado = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=True)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id):
        return Cliente.query.get(id)

    @staticmethod
    def get_all():
        return Cliente.query.all()

    @staticmethod
    def obtener_por_celular(celular):
        return Cliente.query.filter_by(celular=celular).first()

    def get_balance(self):
        transactions = Transaction.get_by_client_id(self.id)
        return sum(t.amount for t in transactions)

    @staticmethod
    def search_by_name(name):
        return Cliente.query.filter(Cliente.nombre_completo.ilike(f"%{name}%")).all()


class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    precio = db.Column(db.Float, nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id):
        return Producto.query.get(id)

    @staticmethod
    def get_all():
        return Producto.query.all()

    @staticmethod
    def get_by_nombre(nombre):
        return Producto.query.filter_by(nombre=nombre).first()


class Pedido(db.Model):
    __tablename__ = 'pedidos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(255), nullable=False, default='pending')
    total = db.Column(db.Float, nullable=False)

    cliente = relationship("Cliente")
    producto = relationship("Producto")

    def calculate_total(self):
        producto = Producto.query.get(self.producto_id)
        self.total = producto.precio * self.cantidad if producto else 0

    def save(self):
        self.calculate_total()
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id):
        return Pedido.query.get(id)

    @staticmethod
    def get_all():
        return Pedido.query.all()

    @staticmethod
    def get_vista(state=None, search=None):
        query = db.session.query(
            Pedido.id.label('pedido_id'),
            Cliente.nombre_completo.label('cliente'),
            Producto.nombre.label('producto'),
            Pedido.cantidad,
            Pedido.estado,
            (Pedido.cantidad * Producto.precio).label('total')
        ).join(Cliente, Pedido.cliente_id == Cliente.id).join(Producto, Pedido.producto_id == Producto.id)

        if state:
            query = query.filter(Pedido.estado == state)
        if search:
            query = query.filter(Cliente.nombre_completo.ilike(f"%{search}%"))

        return [row._asdict() for row in query.all()]

    @staticmethod
    def get_unique_states():
        return [state[0] for state in db.session.query(Pedido.estado).distinct().all()]


class Mensaje(db.Model):
    __tablename__ = 'mensajes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    whatsapp_id = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    direction = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    message_type = db.Column(db.String(50), nullable=False)

    def exists_in_db(self):
        return db.session.query(Mensaje).filter_by(
            whatsapp_id=self.whatsapp_id, message=self.message, timestamp=self.timestamp
        ).first() is not None

    def save(self):
        if not self.exists_in_db():
            db.session.add(self)
            db.session.commit()

    @staticmethod
    def get_all():
        return Mensaje.query.all()


class ClientesList(db.Model):
    __tablename__ = 'listas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def rename(self, nuevo_nombre):
        self.nombre = nuevo_nombre
        self.save()

    def add_cliente(self, cliente_id):
        clientes_listas_entry = ClientesListEntry(lista_id=self.id, cliente_id=cliente_id)
        db.session.add(clientes_listas_entry)
        db.session.commit()

    def remove_cliente(self, cliente_id):
        ClientesListEntry.query.filter_by(lista_id=self.id, cliente_id=cliente_id).delete()
        db.session.commit()

    def delete(self):
        ClientesListEntry.query.filter_by(lista_id=self.id).delete()
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return ClientesList.query.all()

    @staticmethod
    def get_by_id(lista_id):
        return ClientesList.query.get(lista_id)

    def get_clientes(self):
        return Cliente.query.join(ClientesListEntry).filter(ClientesListEntry.lista_id == self.id).all()


class ClientesListEntry(db.Model):
    __tablename__ = 'clientes_listas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lista_id = db.Column(db.Integer, db.ForeignKey('listas.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_client_id(client_id):
        return Transaction.query.filter_by(client_id=client_id).all()

    @staticmethod
    def get_debts_older_than(date):
        return Transaction.query.filter(Transaction.amount < 0, Transaction.date < date).all()

    @staticmethod
    def get_all():
        return Transaction.query.all()


class HojaDeRuta(db.Model):
    __tablename__ = 'hojas_de_ruta'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(255), default='on delivery')

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return HojaDeRuta.query.order_by(HojaDeRuta.fecha.desc()).all()

    @staticmethod
    def get_by_id(hoja_id):
        return HojaDeRuta.query.get(hoja_id)


class HojaDeRutaPedido(db.Model):
    __tablename__ = 'hojas_de_ruta_pedidos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hoja_de_ruta_id = db.Column(db.Integer, db.ForeignKey('hojas_de_ruta.id'), nullable=False)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    posicion = db.Column(db.Integer, nullable=True)
    estado = db.Column(db.String(255), default='on delivery')

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_hoja_id(hoja_de_ruta_id):
        return HojaDeRutaPedido.query.filter_by(hoja_de_ruta_id=hoja_de_ruta_id).order_by(HojaDeRutaPedido.posicion).all()

    @staticmethod
    def get_by_pedido_id_and_hoja_id(pedido_id, hoja_de_ruta_id):
        return HojaDeRutaPedido.query.filter_by(pedido_id=pedido_id, hoja_de_ruta_id=hoja_de_ruta_id).first()

    @staticmethod
    def get_detalle_by_hoja_id(hoja_de_ruta_id):
        query = (
            db.session.query(
                Pedido.id.label('pedido_id'),
                Cliente.nombre_completo.label('cliente'),
                Producto.nombre.label('producto'),
                Pedido.cantidad,
                Pedido.estado,
                Cliente.direccion.label('ubicacion')
            )
            .join(Pedido, HojaDeRutaPedido.pedido_id == Pedido.id)
            .join(Cliente, Pedido.cliente_id == Cliente.id)
            .join(Producto, Pedido.producto_id == Producto.id)
            .filter(HojaDeRutaPedido.hoja_de_ruta_id == hoja_de_ruta_id)
        )
        return query.all()



class Bot:
    def __init__(self, api_key, phone_number_id):
        self.api_key = api_key
        self.phone_number_id = phone_number_id
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def parse_text(self, data):
        """Extracts text from different message types."""
        if data['type'] == 'interactive' and data['interactive']['type'] == 'button_reply':
            return data['interactive']['button_reply']['title']
        elif data['type'] == 'button':
            return data['button']['text']
        else:
            return data['text']['body']  # Default to standard text message

    def parse_number(self, number):
        """Parses and modifies phone number if it starts with a specific prefix."""
        if number.startswith("549"):
            return number[:2] + number[3:]
        return number

    def enviar_saludo(self, cliente: Cliente):
        """Sends a greeting message with product options."""
        url = f"https://graph.facebook.com/v20.0/{self.phone_number_id}/messages"
        saludo_template = {
            "messaging_product": "whatsapp",
            "to": cliente.celular,
            "type": "template",
            "template": {
                "name": "saludo",
                "language": {"code": "es_AR"},
            }
        }
        timestamp = int(time.time())
        try:
            response = requests.post(url, headers=self.headers, json=saludo_template)
            if response.status_code == 200:
                # Log the sent message in the database
                message = Mensaje(
                    whatsapp_id=cliente.celular,
                    message="saludo",
                    direction='sent',
                    timestamp=timestamp,
                    message_type='text'
                )
                db.session.add(message)
                db.session.commit()
                cliente.estado_conversacion = "esperando_producto"
                db.session.commit()
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except requests.RequestException as e:
            print(f"HTTP Request failed: {e}")
            return None

    def enviar_mensaje(self, celular, mensaje):
        """Send a text message to the WhatsApp API and log it in the database."""
        url = f"https://graph.facebook.com/v20.0/{self.phone_number_id}/messages"
        data = {
            "messaging_product": "whatsapp",
            "to": celular,
            "type": "text",
            "text": {
                "body": mensaje
            }
        }
        timestamp = int(time.time())
        try:
            response = requests.post(url, headers=self.headers, json=data)
            if response.status_code == 200:
                message = Mensaje(
                    whatsapp_id=celular,
                    message=mensaje,
                    direction='sent',
                    timestamp=timestamp,
                    message_type='text'
                )
                db.session.add(message)
                db.session.commit()
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except requests.RequestException as e:
            print(f"HTTP Request failed: {e}")
            return None

    def procesar_mensaje(self, data):
        """Processes received message data and performs actions based on conversation state."""
        if 'messages' in data['entry'][0]['changes'][0]['value']:
            message_data = data['entry'][0]['changes'][0]['value']['messages'][0]
            phone_number = self.parse_number(message_data['from'])
            message_text = self.parse_text(message_data)
            timestamp = int(message_data['timestamp'])

            # Log the received message
            message = Mensaje(
                whatsapp_id=phone_number,
                message=message_text,
                direction='received',
                timestamp=timestamp,
                message_type='text'
            )
            db.session.add(message)
            db.session.commit()
            print(f"Received message from {phone_number}: {message_text}")

            cliente = Cliente.obtener_por_celular(phone_number)
            if cliente:
                if cliente.estado_conversacion == "esperando_producto":
                    producto = Producto.get_by_nombre(message_text)
                    if producto:
                        self.preguntar_cantidad(cliente, message_text)
                elif cliente.estado_conversacion == "esperando_cantidad":
                    self.confirmar_pedido(cliente, message_text)

    def preguntar_cantidad(self, cliente: Cliente, producto_nombre):
        """Prompts the client to specify a quantity for the selected product."""
        producto = Producto.get_by_nombre(producto_nombre)
        if producto:
            cliente.producto_seleccionado = producto.id
            cliente.estado_conversacion = "esperando_cantidad"
            db.session.commit()

            mensaje = f"¿Cuántos {producto.nombre} te gustaría ordenar?"
            print(mensaje)
            self.enviar_mensaje(cliente.celular, mensaje)

    def confirmar_pedido(self, cliente: Cliente, cantidad):
        """Creates an order, saves it to the database, and confirms with the client."""
        try:
            pedido = Pedido(cliente_id=cliente.id, producto_id=cliente.producto_seleccionado, cantidad=int(cantidad))
            pedido.save()

            producto = Producto.get_by_id(pedido.producto_id)

            mensaje = f"Gracias {cliente.nombre_completo}, tu pedido de {cantidad} {producto.nombre}(s) ha sido registrado."
            self.enviar_mensaje(cliente.celular, mensaje)

            cliente.estado_conversacion = None
            cliente.producto_seleccionado = None
            db.session.commit()
        except ValueError as e:
            print(f"Error processing quantity: {e}")
            self.enviar_mensaje(cliente.celular, "Hubo un error procesando tu cantidad, intenta de nuevo.")
