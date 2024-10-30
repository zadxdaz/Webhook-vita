from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import requests
import time

# Load environment variables
load_dotenv()
DATABASE = os.getenv('DATABASE', 'sqlite:///vita.db')

# Set up SQLAlchemy engine and session
engine = create_engine(DATABASE,connect_args={'connect_timeout':10},pool_recycle=280)
Session = sessionmaker(bind=engine)
db = SQLAlchemy()

Base = declarative_base(db.Model)

class Cliente(Base):
    __tablename__ = 'clientes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_completo = Column(String(255), nullable=False)  # Specify length
    celular = Column(String(20), nullable=False, unique=True)
    direccion = Column(String(255), nullable=False)
    estado_conversacion = Column(String(50), nullable=True)
    producto_seleccionado = Column(Integer, ForeignKey('productos.id'), nullable=True)
    
    def save(self):
        session = Session()
        try:
            session.add(self)
            session.commit()
        except SQLAlchemyError as e:
            print(f"Error saving cliente: {e}")
            session.rollback()
        finally:
            session.close()

    def delete(self):
        session = Session()
        try:
            session.delete(self)
            session.commit()
        except SQLAlchemyError as e:
            print(f"Error deleting cliente: {e}")
            session.rollback()
        finally:
            session.close()

    @staticmethod
    def get_by_id(id):
        session = Session()
        cliente = session.query(Cliente).filter_by(id=id).first()
        session.close()
        return cliente

    @staticmethod
    def get_all():
        session = Session()
        clientes = session.query(Cliente).all()
        session.close()
        return clientes

    @staticmethod
    def obtener_por_celular(celular):
        session = Session()
        cliente = session.query(Cliente).filter_by(celular=celular).first()
        session.close()
        return cliente

    def get_balance(self):
        transactions = Transaction.get_by_client_id(self.id)
        balance = sum([t.amount for t in transactions])  # Sum the 'amount' field in all transactions
        return balance

    @staticmethod
    def search_by_name(name):
        session = Session()
        query = f"%{name}%"
        clientes = session.query(Cliente).filter(Cliente.nombre_completo.ilike(query)).all()
        session.close()
        return clientes

class Producto(Base):
    __tablename__ = 'productos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)  # Specify length for VARCHAR
    descripcion = Column(Text, nullable=True)
    precio = Column(Float, nullable=False)

    def save(self):
        session = Session()
        try:
            session.add(self)
            session.commit()
        except SQLAlchemyError as e:
            print(f"Error saving producto: {e}")
            session.rollback()
        finally:
            session.close()

    def delete(self):
        session = Session()
        try:
            session.delete(self)
            session.commit()
        except SQLAlchemyError as e:
            print(f"Error deleting producto: {e}")
            session.rollback()
        finally:
            session.close()

    @staticmethod
    def get_by_id(id):
        session = Session()
        producto = session.query(Producto).filter_by(id=id).first()
        session.close()
        return producto

    @staticmethod
    def get_all():
        session = Session()
        productos = session.query(Producto).all()
        session.close()
        return productos

    @staticmethod
    def get_by_nombre(nombre):
        session = Session()
        producto = session.query(Producto).filter_by(nombre=nombre).first()
        session.close()
        return producto

class Pedido(Base):
    __tablename__ = 'pedidos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    producto_id = Column(Integer, ForeignKey('productos.id'), nullable=False)
    cantidad = Column(Integer, nullable=False)
    estado = Column(String(255), nullable=False, default='pending')
    total = Column(Float, nullable=False)

    cliente = relationship("Cliente")
    producto = relationship("Producto")

    def calculate_total(self):
        session = Session()
        producto = session.query(Producto).filter_by(id=self.producto_id).first()
        session.close()
        if producto:
            self.total = float(producto.precio) * int(self.cantidad)

    def save(self):
        self.calculate_total()
        session = Session()
        try:
            session.add(self)
            session.commit()
        except SQLAlchemyError as e:
            print(f"Error saving pedido: {e}")
            session.rollback()
        finally:
            session.close()

    def delete(self):
        session = Session()
        try:
            session.delete(self)
            session.commit()
        except SQLAlchemyError as e:
            print(f"Error deleting pedido: {e}")
            session.rollback()
        finally:
            session.close()

    @staticmethod
    def get_by_id(id):
        session = Session()
        pedido = session.query(Pedido).filter_by(id=id).first()
        session.close()
        return pedido

    @staticmethod
    def get_all():
        session = Session()
        pedidos = session.query(Pedido).all()
        session.close()
        return pedidos

    @staticmethod
    def get_vista(state=None, search=None):
        session = Session()
        try:
            # Start query with Pedido and explicitly join Cliente and Producto
            query = (
                session.query(
                    Pedido.id.label('pedido_id'),
                    Cliente.nombre_completo.label('cliente'),
                    Producto.nombre.label('producto'),
                    Pedido.cantidad,
                    Pedido.estado,
                    (Pedido.cantidad * Producto.precio).label('total')
                )
                .select_from(Pedido)  # Start with Pedido as the FROM clause
                .join(Cliente, Pedido.cliente_id == Cliente.id)  # Explicitly join Cliente on foreign key
                .join(Producto, Pedido.producto_id == Producto.id)  # Explicitly join Producto on foreign key
            )

            # Add filtering by state if provided
            if state:
                query = query.filter(Pedido.estado == state)

            # Filter by client name if a search term is provided
            if search:
                query = query.filter(Cliente.nombre_completo.ilike(f'%{search}%'))

            # Execute query and fetch results
            rows = query.all()
            return [
                {
                    'pedido_id': row.pedido_id,
                    'cliente': row.cliente,
                    'producto': row.producto,
                    'cantidad': row.cantidad,
                    'estado': row.estado,
                    'total': row.total
                }
                for row in rows
            ]
        except SQLAlchemyError as e:
            print(f"Error retrieving pedidos vista: {e}")
        finally:
            session.close()


    @staticmethod
    def get_unique_states():
        session = Session()
        states = session.query(Pedido.estado).distinct().all()
        session.close()
        return [state[0] for state in states]

    @staticmethod
    def get_by_estado(estado):
        session = Session()
        pedidos = session.query(Pedido).filter_by(estado=estado).all()
        session.close()
        return pedidos


class Mensaje(Base):
    __tablename__ = 'mensajes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    whatsapp_id = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    direction = Column(String(10), nullable=False)  # e.g., 'sent' or 'received'
    timestamp = Column(DateTime, default=datetime.now)
    message_type = Column(String(50), nullable=False)  # e.g., 'text', 'image'

    def exists_in_db(self):
        session = Session()
        exists = session.query(Mensaje).filter_by(
            whatsapp_id=self.whatsapp_id, message=self.message, timestamp=self.timestamp
        ).first() is not None
        session.close()
        return exists

    def save(self):
        if self.exists_in_db():
            print("Message already exists in the database, skipping save.")
            return
        session = Session()
        try:
            session.add(self)
            session.commit()
        except SQLAlchemyError as e:
            print(f"Error saving message: {e}")
            session.rollback()
        finally:
            session.close()

    @staticmethod
    def get_all():
        session = Session()
        messages = session.query(Mensaje).all()
        session.close()
        return messages

class ClientesList(Base):
    __tablename__ = 'listas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)  # Specify length

    def save(self):
        session = Session()
        try:
            session.add(self)
            session.commit()
        except SQLAlchemyError as e:
            print(f"Error saving list: {e}")
            session.rollback()
        finally:
            session.close()

    def rename(self, nuevo_nombre):
        self.nombre = nuevo_nombre
        self.save()

    def add_cliente(self, cliente_id):
        session = Session()
        try:
            clientes_listas_entry = ClientesListEntry(lista_id=self.id, cliente_id=cliente_id)
            session.add(clientes_listas_entry)
            session.commit()
        except SQLAlchemyError as e:
            print(f"Error adding cliente to list: {e}")
            session.rollback()
        finally:
            session.close()

    def remove_cliente(self, cliente_id):
        session = Session()
        try:
            session.query(ClientesListEntry).filter_by(lista_id=self.id, cliente_id=cliente_id).delete()
            session.commit()
        except SQLAlchemyError as e:
            print(f"Error removing cliente from list: {e}")
            session.rollback()
        finally:
            session.close()

    def delete(self):
        session = Session()
        try:
            session.query(ClientesListEntry).filter_by(lista_id=self.id).delete()
            session.delete(self)
            session.commit()
        except SQLAlchemyError as e:
            print(f"Error deleting list: {e}")
            session.rollback()
        finally:
            session.close()

    @staticmethod
    def get_all():
        session = Session()
        listas = session.query(ClientesList).all()
        session.close()
        return listas

    @staticmethod
    def get_by_id(lista_id):
        session = Session()
        lista = session.query(ClientesList).filter_by(id=lista_id).first()
        session.close()
        return lista

    def get_clientes(self):
        """Retrieve all clients in the list."""
        session = Session()
        try:
            clientes = session.query(Cliente).join(ClientesListEntry).filter(ClientesListEntry.lista_id == self.id).all()
            return clientes
        except SQLAlchemyError as e:
            print(f"Error retrieving clients in list: {e}")
        finally:
            session.close()


class ClientesListEntry(Base):
    __tablename__ = 'clientes_listas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    lista_id = Column(Integer, ForeignKey('listas.id'), nullable=False)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)

    def save(self):
        session = Session()
        try:
            session.add(self)
            session.commit()
        except SQLAlchemyError as e:
            print(f"Error saving transaction: {e}")
            session.rollback()
        finally:
            session.close()

    @staticmethod
    def get_by_client_id(client_id):
        session = Session()
        transactions = session.query(Transaction).filter_by(client_id=client_id).all()
        session.close()
        return transactions

    @staticmethod
    def get_debts_older_than(date):
        session = Session()
        debts = session.query(Transaction).filter(Transaction.amount < 0, Transaction.date < date).all()
        session.close()
        return debts
    
    @staticmethod
    def get_all():
        session = Session()
        transactions = session.query(Transaction).all()
        session.close()
        return transactions


class HojaDeRuta(Base):
    __tablename__ = 'hojas_de_ruta'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    estado = Column(String(255), default='on delivery')

    def save(self):
        session = Session()
        try:
            session.add(self)
            session.commit()
        except SQLAlchemyError as e:
            print(f"Error saving Hoja de Ruta: {e}")
            session.rollback()
        finally:
            session.close()

    @staticmethod
    def get_all():
        session = Session()
        hojas = session.query(HojaDeRuta).order_by(HojaDeRuta.fecha.desc()).all()
        session.close()
        return hojas
    
    @staticmethod
    def get_by_id(hoja_id):
        session = Session()
        hoja = session.query(HojaDeRuta).filter_by(id=hoja_id).first()
        session.close()
        return hoja


class HojaDeRutaPedido(Base):
    __tablename__ = 'hojas_de_ruta_pedidos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    hoja_de_ruta_id = Column(Integer, ForeignKey('hojas_de_ruta.id'), nullable=False)
    pedido_id = Column(Integer, ForeignKey('pedidos.id'), nullable=False)
    posicion = Column(Integer, nullable=True)
    estado = Column(String(255), default='on delivery')

    def save(self):
        session = Session()
        try:
            session.add(self)
            session.commit()
        except SQLAlchemyError as e:
            print(f"Error saving HojaDeRutaPedido: {e}")
            session.rollback()
        finally:
            session.close()

    @staticmethod
    def get_by_hoja_id(hoja_de_ruta_id):
        session = Session()
        pedidos = session.query(HojaDeRutaPedido).filter_by(hoja_de_ruta_id=hoja_de_ruta_id).order_by(HojaDeRutaPedido.posicion).all()
        session.close()
        return pedidos

    @staticmethod
    def get_by_pedido_id_and_hoja_id(pedido_id, hoja_de_ruta_id):
        session = Session()
        entry = session.query(HojaDeRutaPedido).filter_by(
            pedido_id=pedido_id, hoja_de_ruta_id=hoja_de_ruta_id
        ).first()
        session.close()
        return entry
    
    @staticmethod
    def get_detalle_by_hoja_id(hoja_de_ruta_id):
        session = Session()
        detalles = session.query(HojaDeRutaPedido).filter_by(hoja_de_ruta_id=hoja_de_ruta_id).all()
        session.close()
        return detalles



class Bot:
    def __init__(self, api_key, phone_number_id):
        self.api_key = api_key
        self.phone_number_id = phone_number_id
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def parse_text(self,data):
        if data['type'] == 'interactive' and data['interactive']['type'] == 'button_reply':
            text = data['interactive']['button_reply']['title']
        elif data['type'] == 'button':
            text = data['button']['text']
        else:
            text = data['text']['body']  # Texto del mensaje

        return text

    def parse_number(self,number):
        if number[:3] == "549":
            test = number[:2]
            aux = number[3:]
            number=test + aux
        return number

    def enviar_saludo(self, cliente:Cliente):
        url = f"https://graph.facebook.com/v20.0/{self.phone_number_id}/messages"
        # Enviar un mensaje de saludo con opciones de productos
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
        print(cliente.celular)
        try:
            response = requests.post(url, headers=self.headers, json=saludo_template)
            if response.status_code == 200:
                # Log the sent message to the database
                
                message = Mensaje(
                    whatsapp_id=cliente.celular,
                    message="saludo",
                    direction='sent',
                    timestamp=timestamp,
                    message_type='text'
                )
                message.save()
                cliente.estado_conversacion = "esperando_producto"
                cliente.save()
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except requests.RequestException as e:
            print(f"HTTP Request failed: {e}")
            return None

    def enviar_mensaje(self, celular, mensaje):
        """Send a message to the WhatsApp API and log it in the database."""
        url = f"https://graph.facebook.com/v20.0/{self.phone_number_id}/messages"
        data = {
            "messaging_product": "whatsapp",
            "to": celular,  # Phone number with country code, without leading '+'
            "type": "text",
            "text": {
                "body": mensaje
            }
        }
        timestamp = int(time.time())
        try:
            response = requests.post(url, headers=self.headers, json=data)
            if response.status_code == 200:
                # Log the sent message to the database
                message = Mensaje(
                    whatsapp_id=celular,
                    message=mensaje,
                    direction='sent',
                    timestamp=timestamp,
                    message_type='text'
                )
                message.save()
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except requests.RequestException as e:
            print(f"HTTP Request failed: {e}")
            return None

    def procesar_mensaje(self, data):
        # Procesar la respuesta del cliente
        if 'messages' in data['entry'][0]['changes'][0]['value']:
            message_data = data['entry'][0]['changes'][0]['value']['messages'][0]
            phone_number = self.parse_number(message_data['from'])
            message_text = self.parse_text(message_data)
            timestamp = message_data['timestamp']

            # Log the received message to the database
            message = Mensaje(
                whatsapp_id=phone_number,
                message=message_text,
                direction='received',
                timestamp=timestamp,
                message_type='text'
            )
            message.save()
            print(f"Received message from {phone_number}: {message_text}")

            # Buscar cliente por su número de celular
            cliente = Cliente.obtener_por_celular(phone_number)
            if cliente:
                if cliente.estado_conversacion == "esperando_producto":
                    producto = Producto.get_by_nombre(message_text)
                    if producto:
                        self.preguntar_cantidad(cliente, message_text)
                elif cliente.estado_conversacion == "esperando_cantidad":
                    self.confirmar_pedido(cliente, message_text)
            

    def preguntar_cantidad(self, cliente:Cliente, producto_nombre):
        # Actualizar el estado del cliente a "esperando_cantidad"
        producto = Producto.get_by_nombre(producto_nombre)
        cliente.producto_seleccionado = producto.id
        cliente.estado_conversacion = "esperando_cantidad"
        cliente.save()

        mensaje = f"¿Cuántos {producto.nombre} te gustaría ordenar?"
        print(mensaje)
        self.enviar_mensaje(cliente.celular,mensaje)

    def confirmar_pedido(self, cliente:Cliente, cantidad):
        # Crear un pedido en el sistema
        pedido =Pedido(cliente.id, cliente.producto_seleccionado, cantidad)
        pedido.save()

        producto = Producto.get_by_id(pedido.producto_id)

        # Enviar confirmación al cliente
        mensaje =  f"Gracias {cliente.nombre_completo}, tu pedido de {cantidad} {producto.nombre}(s) ha sido registrado."
        self.enviar_mensaje(cliente.celular,mensaje)

        # Resetear el estado de la conversación del cliente
        cliente.estado_conversacion = None
        cliente.producto_seleccionado = None
        cliente.save()

# Creating tables
#Base.metadata.create_all(engine)
