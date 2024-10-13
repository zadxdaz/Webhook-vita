import sqlite3
import requests
import time


DATABASE = 'vita.db'

import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE = os.getenv('DATABASE', 'vita.db')

class BaseModel:
    """Base class for handling database connections and common operations."""
    
    @staticmethod
    def get_db_connection():
        """Establish a connection to the SQLite database."""
        try:
            conn = sqlite3.connect(DATABASE)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            print(f"Error connecting to the database: {e}")
            raise

    @staticmethod
    def close_connection(conn):
        """Close the connection to the database."""
        if conn:
            try:
                conn.close()
            except sqlite3.Error as e:
                print(f"Error closing the database connection: {e}")

class Cliente(BaseModel):
    def __init__(self, nombre_completo, celular, direccion, id=None, estado_conversacion=None, producto_seleccionado=None):
        self.id = id
        self.nombre_completo = nombre_completo
        self.celular = celular
        self.direccion = direccion
        self.estado_conversacion = estado_conversacion
        self.producto_seleccionado = producto_seleccionado

    def save(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            if self.id:
                cursor.execute('''
                    UPDATE clientes
                    SET nombre_completo = ?, celular = ?, direccion = ?, estado_conversacion = ?, producto_seleccionado = ?
                    WHERE id = ?
                ''', (self.nombre_completo, self.celular, self.direccion, self.estado_conversacion, self.producto_seleccionado, self.id))
            else:
                cursor.execute('''
                    INSERT INTO clientes (nombre_completo, celular, direccion, estado_conversacion, producto_seleccionado)
                    VALUES (?, ?, ?, ?, ?)
                ''', (self.nombre_completo, self.celular, self.direccion, self.estado_conversacion, self.producto_seleccionado))
                self.id = cursor.lastrowid
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving cliente: {e}")
            conn.rollback()
        finally:
            self.close_connection(conn)

    def delete(self):
        if self.id:
            conn = self.get_db_connection()
            try:
                conn.execute('DELETE FROM clientes WHERE id = ?', (self.id,))
                conn.commit()
            except sqlite3.Error as e:
                print(f"Error deleting cliente: {e}")
                conn.rollback()
            finally:
                self.close_connection(conn)

    @staticmethod
    def get_by_id(id):
        conn = Cliente.get_db_connection()
        try:
            cliente_row = conn.execute('SELECT * FROM clientes WHERE id = ?', (id,)).fetchone()
            if cliente_row:
                return Cliente(cliente_row['nombre_completo'], cliente_row['celular'], cliente_row['direccion'],
                               cliente_row['id'], cliente_row['estado_conversacion'], cliente_row['producto_seleccionado'])
        except sqlite3.Error as e:
            print(f"Error retrieving cliente: {e}")
        finally:
            Cliente.close_connection(conn)
        return None

    @staticmethod
    def get_all():
        conn = Cliente.get_db_connection()
        try:
            clientes = conn.execute('SELECT * FROM clientes').fetchall()
            return [Cliente(cliente['nombre_completo'], cliente['celular'], cliente['direccion'], cliente['id'],
                            cliente['estado_conversacion'], cliente['producto_seleccionado']) for cliente in clientes]
        except sqlite3.Error as e:
            print(f"Error retrieving all clientes: {e}")
        finally:
            Cliente.close_connection(conn)
        return []

    @staticmethod
    def obtener_por_celular(celular):
        conn = Cliente.get_db_connection()
        try:
            row = conn.execute("SELECT * FROM clientes WHERE celular = ?", (celular,)).fetchone()
            if row:
                return Cliente(
                    nombre_completo=row['nombre_completo'],
                    celular=row['celular'],
                    direccion=row['direccion'],
                    id=row['id'],
                    estado_conversacion=row['estado_conversacion'],
                    producto_seleccionado=row['producto_seleccionado']
                )
        except sqlite3.Error as e:
            print(f"Error retrieving cliente by celular: {e}")
        finally:
            Cliente.close_connection(conn)
        return None

class Producto(BaseModel):
    def __init__(self, nombre, descripcion, precio, id=None):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio

    def save(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            if self.id:
                cursor.execute('''
                    UPDATE productos
                    SET nombre = ?, descripcion = ?, precio = ?
                    WHERE id = ?
                ''', (self.nombre, self.descripcion, self.precio, self.id))
            else:
                cursor.execute('''
                    INSERT INTO productos (nombre, descripcion, precio)
                    VALUES (?, ?, ?)
                ''', (self.nombre, self.descripcion, self.precio))
                self.id = cursor.lastrowid
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving producto: {e}")
            conn.rollback()
        finally:
            self.close_connection(conn)

    def delete(self):
        if self.id:
            conn = self.get_db_connection()
            try:
                conn.execute('DELETE FROM productos WHERE id = ?', (self.id,))
                conn.commit()
            except sqlite3.Error as e:
                print(f"Error deleting producto: {e}")
                conn.rollback()
            finally:
                self.close_connection(conn)

    @staticmethod
    def get_by_id(id):
        conn = Producto.get_db_connection()
        try:
            producto_row = conn.execute('SELECT * FROM productos WHERE id = ?', (id,)).fetchone()
            if producto_row:
                return Producto(producto_row['nombre'], producto_row['descripcion'], producto_row['precio'], producto_row['id'])
        except sqlite3.Error as e:
            print(f"Error retrieving producto: {e}")
        finally:
            Producto.close_connection(conn)
        return None

    @staticmethod
    def get_all():
        conn = Producto.get_db_connection()
        try:
            productos = conn.execute('SELECT * FROM productos').fetchall()
            return [Producto(producto['nombre'], producto['descripcion'], producto['precio'], producto['id']) for producto in productos]
        except sqlite3.Error as e:
            print(f"Error retrieving all productos: {e}")
        finally:
            Producto.close_connection(conn)
        return []

    @staticmethod
    def get_by_nombre(nombre):
        conn = Producto.get_db_connection()
        try:
            # Query the database for a product matching the given name
            producto_row = conn.execute('SELECT * FROM productos WHERE nombre = ?', (nombre,)).fetchone()
            if producto_row:
                # If a product is found, return an instance of Producto
                return Producto(
                    nombre=producto_row['nombre'],
                    descripcion=producto_row['descripcion'],
                    precio=producto_row['precio'],
                    id=producto_row['id']
                )
            else:
                # If no product is found, return False
                return None
        except sqlite3.Error as e:
            print(f"Error retrieving product by name: {e}")
            return None
        finally:
            Producto.close_connection(conn)
class Pedido(BaseModel):
    def __init__(self, cliente_id, producto_id, cantidad, estado=None, id=None):
        self.id = id
        self.cliente_id = cliente_id
        self.producto_id = producto_id
        self.cantidad = cantidad
        self.estado = estado

    def save(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            if self.id:
                cursor.execute('''
                    UPDATE pedidos
                    SET cliente_id = ?, producto_id = ?, cantidad = ?, estado = ?
                    WHERE id = ?
                ''', (self.cliente_id, self.producto_id, self.cantidad, self.estado, self.id))
            else:
                cursor.execute('''
                    INSERT INTO pedidos (cliente_id, producto_id, cantidad, estado)
                    VALUES (?, ?, ?, ?)
                ''', (self.cliente_id, self.producto_id, self.cantidad, self.estado))
                self.id = cursor.lastrowid
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving pedido: {e}")
            conn.rollback()
        finally:
            self.close_connection(conn)

    def delete(self):
        if self.id:
            conn = self.get_db_connection()
            try:
                conn.execute('DELETE FROM pedidos WHERE id = ?', (self.id,))
                conn.commit()
            except sqlite3.Error as e:
                print(f"Error deleting pedido: {e}")
                conn.rollback()
            finally:
                self.close_connection(conn)

    @staticmethod
    def get_by_id(id):
        conn = Pedido.get_db_connection()
        try:
            pedido_row = conn.execute('SELECT * FROM pedidos WHERE id = ?', (id,)).fetchone()
            if pedido_row:
                return Pedido(pedido_row['cliente_id'], pedido_row['producto_id'], pedido_row['cantidad'], pedido_row['estado'], pedido_row['id'])
        except sqlite3.Error as e:
            print(f"Error retrieving pedido: {e}")
        finally:
            Pedido.close_connection(conn)
        return None

    @staticmethod
    def get_all():
        conn = Pedido.get_db_connection()
        try:
            pedidos = conn.execute('SELECT * FROM pedidos').fetchall()
            return [Pedido(pedido['cliente_id'], pedido['producto_id'], pedido['cantidad'], pedido['estado'], pedido['id']) for pedido in pedidos]
        except sqlite3.Error as e:
            print(f"Error retrieving all pedidos: {e}")
        finally:
            Pedido.close_connection(conn)
        return []

    @staticmethod
    def get_vista():
        conn = Pedido.get_db_connection()
        try:
            pedidos = conn.execute("""
                SELECT c.nombre_completo as nombre , pro.nombre as producto, p.cantidad as cantidad, p.estado as estado, p.id as id, pro.precio * p.cantidad as total
                FROM pedidos AS p
                JOIN clientes AS c ON p.cliente_id = c.id
                JOIN productos AS pro ON p.producto_id = pro.id
            """).fetchall()
            return pedidos
        except sqlite3.Error as e:
            print(f"Error retrieving pedido vista: {e}")
        finally:
            Pedido.close_connection(conn)
        return []


class HojaDeRuta:
    def __init__(self, pedidos):
        self.pedidos = pedidos
        self.rutas = []

    def generar_ruta(self):
        # Ordena los pedidos por dirección o alguna lógica para optimizar la ruta
        self.rutas = sorted(self.pedidos, key=lambda pedido: pedido['direccion'])
    
    def mostrar_ruta(self):
        # Muestra la hoja de ruta
        for pedido in self.rutas:
            cliente = Cliente.obtener_por_celular(pedido['cliente_celular'])
            print(f"Cliente: {cliente[1]} - Dirección: {cliente[3]} - Pedido: {pedido['productos']}")

    def actualizar_estado_pedido(self, pedido_id, nuevo_estado):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            UPDATE pedidos
            SET estado = ?
            WHERE id = ?
        ''', (nuevo_estado, pedido_id))
        db.commit()

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
        self.enviar_mensaje(saludo_template)
        cliente.estado_conversacion = "esperando_producto"
        cliente.save()

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

        mensaje = {
            "messaging_product": "whatsapp",
            "to": cliente.celular,
            "type": "text",
            "text": {
                "body": f"¿Cuántos {producto.nombre}s te gustaría ordenar?"
            }
        }
        self.enviar_mensaje(mensaje)

    def confirmar_pedido(self, cliente:Cliente, cantidad):
        # Crear un pedido en el sistema
        pedido =Pedido(cliente.id, cliente.producto_seleccionado, cantidad)
        pedido.save()

        producto = Producto.get_by_id(pedido.producto_id)

        # Enviar confirmación al cliente
        mensaje = {
            "messaging_product": "whatsapp",
            "to": cliente.celular,
            "type": "text",
            "text": {
                "body": f"Gracias {cliente.nombre_completo}, tu pedido de {cantidad} {producto.nombre}(s) ha sido registrado."
            }
        }
        self.enviar_mensaje(cliente.celular,mensaje)

        # Resetear el estado de la conversación del cliente
        cliente.estado_conversacion = None
        cliente.producto_seleccionado = None
        cliente.save()

class Mensaje(BaseModel):
    def __init__(self, whatsapp_id, message, direction, timestamp, message_type, id=None):
        self.id = id
        self.whatsapp_id = whatsapp_id
        self.message = message
        self.direction = direction  # 'sent' or 'received'
        self.timestamp = timestamp
        self.message_type = message_type  # e.g., 'text', 'image'

    def exists_in_db(self):
        """Check if the message already exists in the database."""
        conn = self.get_db_connection()
        try:
            cursor = conn.execute('''
                SELECT 1 FROM mensajes 
                WHERE whatsapp_id = ? AND message = ? AND timestamp = ?
            ''', (self.whatsapp_id, self.message, self.timestamp))
            
            return cursor.fetchone() is not None  # Returns True if the message exists, False otherwise
        except sqlite3.Error as e:
            print(f"Error checking if message exists: {e}")
            return False
        finally:
            self.close_connection(conn)

    def save(self):
        """Save the message to the database if it doesn't already exist."""
        if self.exists_in_db():
            print("Message already exists in the database, skipping save.")
            return  # Skip saving if the message already exists

        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO mensajes (whatsapp_id, message, direction, timestamp, type)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.whatsapp_id, self.message, self.direction, self.timestamp, self.message_type))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving message: {e}")
            conn.rollback()
        finally:
            self.close_connection(conn)

    @staticmethod
    def get_all():
        """Retrieve all messages from the database."""
        conn = Mensaje.get_db_connection()
        try:
            messages = conn.execute('SELECT * FROM mensajes').fetchall()
            return messages
        except sqlite3.Error as e:
            print(f"Error retrieving messages: {e}")
        finally:
            Mensaje.close_connection(conn)
        return []
