from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv

from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime


# Load environment variables
load_dotenv()
DATABASE = os.getenv('DATABASE', 'sqlite:///vita.db')

# Set up SQLAlchemy engine and session
engine = create_engine(DATABASE, echo=True)
Session = sessionmaker(bind=engine)

Base = declarative_base()

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
            self.total = producto.precio * self.cantidad

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
        query = session.query(
            Pedido.id.label('pedido_id'),
            Cliente.nombre_completo.label('cliente'),
            Producto.nombre.label('producto'),
            Pedido.cantidad,
            Pedido.estado,
            (Pedido.cantidad * Producto.precio).label('total')
        ).join(Cliente).join(Producto)

        if state:
            query = query.filter(Pedido.estado == state)
        if search:
            query = query.filter(Cliente.nombre_completo.ilike(f'%{search}%'))

        rows = query.all()
        session.close()
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


# Creating tables
Base.metadata.create_all(engine)
