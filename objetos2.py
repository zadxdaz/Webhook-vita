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
    
    def get_balance(self):
        transactions = Transaction.get_by_client_id(self.id)
        balance = sum([t.amount for t in transactions])  # Sum the 'amount' field in all transactions
        return balance
    
    @staticmethod
    def search_by_name(name):
        conn = Cliente.get_db_connection()
        try:
            # Search clients whose name contains the search query (case-insensitive)
            query = '%' + name + '%'
            rows = conn.execute('SELECT * FROM clientes WHERE nombre_completo LIKE ?', (query,)).fetchall()
            return [Cliente(row['nombre_completo'], row['celular'], row['direccion'], row['id'], row['estado_conversacion'], row['producto_seleccionado']) for row in rows]
        except sqlite3.Error as e:
            print(f"Error searching clients: {e}")
        finally:
            Cliente.close_connection(conn)
        return []

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
    def __init__(self, cliente_id, producto_id, cantidad, estado='pending', id=None):
        self.id = id
        self.cliente_id = cliente_id
        self.producto_id = producto_id
        self.cantidad = cantidad
        self.estado = estado
        self.total = self.calculate_total()  # Automatically calculate total based on product price

    def calculate_total(self):
        """Calculate the total price of the Pedido based on the product's price."""
        conn = self.get_db_connection()
        try:
            product = conn.execute('SELECT precio FROM productos WHERE id = ?', (self.producto_id,)).fetchone()
            if product:
                return float(product['precio']) * int(self.cantidad)
            else:
                return 0  # Default to 0 if product not found
        except sqlite3.Error as e:
            print(f"Error calculating total: {e}")
        finally:
            self.close_connection(conn)

    def save(self):
        """Save or update the Pedido in the database."""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            if self.id:
                cursor.execute('''
                    UPDATE pedidos
                    SET cliente_id = ?, producto_id = ?, cantidad = ?, estado = ?, total = ?
                    WHERE id = ?
                ''', (self.cliente_id, self.producto_id, self.cantidad, self.estado, self.total, self.id))
            else:
                cursor.execute('''
                    INSERT INTO pedidos (cliente_id, producto_id, cantidad, estado, total)
                    VALUES (?, ?, ?, ?, ?)
                ''', (self.cliente_id, self.producto_id, self.cantidad, self.estado, self.total))
                self.id = cursor.lastrowid  # Get the last inserted ID
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving pedido: {e}")
            conn.rollback()
        finally:
            self.close_connection(conn)

    def update_estado(self, new_estado):
        """Update the estado (status) of the Pedido."""
        self.estado = new_estado
        self.save()

    def delete(self):
        """Delete the Pedido from the database."""
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
        """Retrieve a Pedido by its ID."""
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
        """Retrieve all Pedidos."""
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
        """Retrieve a detailed view of Pedidos, including client names and product details."""
        conn = Pedido.get_db_connection()
        try:
            pedidos = conn.execute('''
                SELECT c.nombre_completo as nombre, pro.nombre as producto, p.cantidad as cantidad, p.estado as estado, p.id as id, pro.precio * p.cantidad as total
                FROM pedidos AS p
                JOIN clientes AS c ON p.cliente_id = c.id
                JOIN productos AS pro ON p.producto_id = pro.id
            ''').fetchall()
            return pedidos
        except sqlite3.Error as e:
            print(f"Error retrieving pedido vista: {e}")
        finally:
            Pedido.close_connection(conn)
        return []

    @staticmethod
    def get_by_estado(estado):
        """Retrieve all Pedidos by their estado (status)."""
        conn = Pedido.get_db_connection()
        try:
            pedidos = conn.execute('SELECT * FROM pedidos WHERE estado = ?', (estado,)).fetchall()
            return [Pedido(pedido['cliente_id'], pedido['producto_id'], pedido['cantidad'], pedido['estado'], pedido['id']) for pedido in pedidos]
        except sqlite3.Error as e:
            print(f"Error retrieving pedidos by estado: {e}")
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

class ClientesList(BaseModel):
    def __init__(self, nombre, id=None):
        self.id = id
        self.nombre = nombre

    def save(self):
        """Create or update a client list in the database."""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            if self.id:
                cursor.execute('''
                    UPDATE listas
                    SET nombre = ?
                    WHERE id = ?
                ''', (self.nombre, self.id))
            else:
                cursor.execute('''
                    INSERT INTO listas (nombre)
                    VALUES (?)
                ''', (self.nombre,))
                self.id = cursor.lastrowid
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving list: {e}")
            conn.rollback()
        finally:
            self.close_connection(conn)

    def rename(self, nuevo_nombre):
        """Rename the list."""
        self.nombre = nuevo_nombre
        self.save()

    def add_cliente(self, cliente_id):
        """Add a client to the list."""
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO clientes_listas (lista_id, cliente_id)
                VALUES (?, ?)
            ''', (self.id, cliente_id))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding cliente to list: {e}")
            conn.rollback()
        finally:
            self.close_connection(conn)

    def remove_cliente(self, cliente_id):
        """Remove a client from the list."""
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM clientes_listas
                WHERE lista_id = ? AND cliente_id = ?
            ''', (self.id, cliente_id))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error removing cliente from list: {e}")
            conn.rollback()
        finally:
            self.close_connection(conn)

    def get_clientes(self):
        """Retrieve all clients in the list."""
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            clientes = cursor.execute('''
                SELECT c.*
                FROM clientes_listas cl
                JOIN clientes c ON cl.cliente_id = c.id
                WHERE cl.lista_id = ?
            ''', (self.id,)).fetchall()

            return [Cliente(
                nombre_completo=row['nombre_completo'],
                celular=row['celular'],
                direccion=row['direccion'],
                id=row['id'],
                estado_conversacion=row['estado_conversacion'],
                producto_seleccionado=row['producto_seleccionado']
            ) for row in clientes]
        except sqlite3.Error as e:
            print(f"Error retrieving clients in list: {e}")
        finally:
            self.close_connection(conn)
        return []

    def delete(self):
        """Delete the list and remove all associated clients."""
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM clientes_listas WHERE lista_id = ?', (self.id,))
            cursor.execute('DELETE FROM listas WHERE id = ?', (self.id,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error deleting list: {e}")
            conn.rollback()
        finally:
            self.close_connection(conn)

    @staticmethod
    def get_all():
        """Retrieve all client lists from the database."""
        conn = ClientesList.get_db_connection()
        try:
            cursor = conn.cursor()
            rows = cursor.execute('SELECT * FROM listas').fetchall()
            return [ClientesList(row['nombre'], row['id']) for row in rows]
        except sqlite3.Error as e:
            print(f"Error retrieving client lists: {e}")
        finally:
            ClientesList.close_connection(conn)
        return []

    @staticmethod
    def get_by_id(lista_id):
        """Retrieve a client list by its ID."""
        conn = ClientesList.get_db_connection()
        try:
            cursor = conn.cursor()
            row = cursor.execute('SELECT * FROM listas WHERE id = ?', (lista_id,)).fetchone()
            if row:
                return ClientesList(row['nombre'], row['id'])
            else:
                return None  # No list found with the given ID
        except sqlite3.Error as e:
            print(f"Error retrieving client list by ID: {e}")
        finally:
            ClientesList.close_connection(conn)
        return None
    
class Transaction(BaseModel):
    def __init__(self, client_id, amount, description=None, date=None, id=None):
        self.id = id
        self.client_id = client_id
        self.amount = amount
        self.description = description
        self.date = date

    def save(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO transactions (client_id, amount, description, date)
                VALUES (?, ?, ?, ?)
            ''', (self.client_id, self.amount, self.description, self.date))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving transaction: {e}")
            conn.rollback()
        finally:
            self.close_connection(conn)

    @staticmethod
    def get_by_client_id(client_id):
        conn = Transaction.get_db_connection()
        try:
            # Fetch transactions from the database
            rows = conn.execute('SELECT * FROM transactions WHERE client_id = ?', (client_id,)).fetchall()
            
            # Convert rows to Transaction objects
            transactions = [
                Transaction(
                    id=row['id'],
                    client_id=row['client_id'],
                    amount=row['amount'],
                    date=row['date'],
                    description=row['description'],
                ) for row in rows
            ]
            return transactions
        except sqlite3.Error as e:
            print(f"Error retrieving transactions: {e}")
        finally:
            Transaction.close_connection(conn)
        return []

    @staticmethod
    def get_debts_older_than(date):
        conn = Transaction.get_db_connection()
        try:
            rows = conn.execute('''
                SELECT * FROM transactions
                WHERE amount < 0 AND date < ?
            ''', (date,)).fetchall()
            return [Transaction(row['client_id'], row['amount'], row['description'], row['date'], row['id']) for row in rows]
        except sqlite3.Error as e:
            print(f"Error retrieving old debts: {e}")
        finally:
            Transaction.close_connection(conn)
        return []

    @staticmethod
    def get_all():
        conn = Transaction.get_db_connection()
        try:
            rows = conn.execute('SELECT * FROM transactions').fetchall()
            return [Transaction(row['client_id'], row['amount'], row['description'], row['date'], row['id']) for row in rows]
        except sqlite3.Error as e:
            print(f"Error retrieving transactions: {e}")
        finally:
            Transaction.close_connection(conn)
        return []

class HojaDeRuta(BaseModel):
    def __init__(self, id=None, fecha=None, estado='on delivery'):
        self.id = id
        self.fecha = fecha
        self.estado = estado

    def save(self):
        """Save the Hoja de Ruta to the database."""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            if self.id:
                cursor.execute('''
                    UPDATE hojas_de_ruta
                    SET estado = ?
                    WHERE id = ?
                ''', (self.estado, self.id))
            else:
                cursor.execute('''
                    INSERT INTO hojas_de_ruta (fecha, estado)
                    VALUES (CURRENT_TIMESTAMP, ?)
                ''', (self.estado,))
                self.id = cursor.lastrowid  # Get the last inserted ID
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving Hoja de Ruta: {e}")
            conn.rollback()
        finally:
            self.close_connection(conn)

    @staticmethod
    def get_by_id(hoja_id):
        """Retrieve a Hoja de Ruta by its ID."""
        conn = HojaDeRuta.get_db_connection()
        try:
            row = conn.execute('SELECT * FROM hojas_de_ruta WHERE id = ?', (hoja_id,)).fetchone()
            if row:
                return HojaDeRuta(id=row['id'], fecha=row['fecha'], estado=row['estado'])
        except sqlite3.Error as e:
            print(f"Error retrieving Hoja de Ruta: {e}")
        finally:
            HojaDeRuta.close_connection(conn)
        return None
    
    @staticmethod
    def get_all():
        """Retrieve all Hojas de Ruta from the database."""
        conn = HojaDeRuta.get_db_connection()
        try:
            rows = conn.execute('SELECT * FROM hojas_de_ruta ORDER BY fecha DESC').fetchall()
            return [HojaDeRuta(id=row['id'], fecha=row['fecha'], estado=row['estado']) for row in rows]
        except sqlite3.Error as e:
            print(f"Error retrieving all Hojas de Ruta: {e}")
        finally:
            HojaDeRuta.close_connection(conn)
        return []

class HojaDeRutaPedido(BaseModel):
    def __init__(self, hoja_de_ruta_id, pedido_id, posicion=None, estado='on delivery', id=None):
        self.id = id
        self.hoja_de_ruta_id = hoja_de_ruta_id
        self.pedido_id = pedido_id
        self.posicion = posicion
        self.estado = estado

    def save(self):
        """Save the HojaDeRutaPedido to the database."""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            if self.id:
                cursor.execute('''
                    UPDATE hojas_de_ruta_pedidos
                    SET posicion = ?, estado = ?
                    WHERE id = ?
                ''', (self.posicion, self.estado, self.id))
            else:
                cursor.execute('''
                    INSERT INTO hojas_de_ruta_pedidos (hoja_de_ruta_id, pedido_id, posicion, estado)
                    VALUES (?, ?, ?, ?)
                ''', (self.hoja_de_ruta_id, self.pedido_id, self.posicion, self.estado))
                self.id = cursor.lastrowid
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving HojaDeRutaPedido: {e}")
            conn.rollback()
        finally:
            self.close_connection(conn)

    @staticmethod
    def get_by_hoja_id(hoja_de_ruta_id):
        """Retrieve all Pedidos for a specific Hoja de Ruta."""
        conn = HojaDeRutaPedido.get_db_connection()
        try:
            rows = conn.execute('''
                SELECT * FROM hojas_de_ruta_pedidos
                WHERE hoja_de_ruta_id = ?
                ORDER BY posicion ASC
            ''', (hoja_de_ruta_id,)).fetchall()
            return [HojaDeRutaPedido(
                        hoja_de_ruta_id=row['hoja_de_ruta_id'],
                        pedido_id=row['pedido_id'],
                        posicion=row['posicion'],
                        estado=row['estado'],
                        id=row['id']
                    ) for row in rows]
        except sqlite3.Error as e:
            print(f"Error retrieving HojaDeRutaPedidos: {e}")
        finally:
            HojaDeRutaPedido.close_connection(conn)
        return []

    @staticmethod
    def get_by_pedido_id_and_hoja_id(pedido_id, hoja_de_ruta_id):
        """Retrieve a specific Pedido in a Hoja de Ruta."""
        conn = HojaDeRutaPedido.get_db_connection()
        try:
            row = conn.execute('''
                SELECT * FROM hojas_de_ruta_pedidos
                WHERE pedido_id = ? AND hoja_de_ruta_id = ?
            ''', (pedido_id, hoja_de_ruta_id)).fetchone()
            if row:
                return HojaDeRutaPedido(
                    hoja_de_ruta_id=row['hoja_de_ruta_id'],
                    pedido_id=row['pedido_id'],
                    posicion=row['posicion'],
                    estado=row['estado'],
                    id=row['id']
                )
        except sqlite3.Error as e:
            print(f"Error retrieving HojaDeRutaPedido: {e}")
        finally:
            HojaDeRutaPedido.close_connection(conn)
        return None

    @staticmethod
    def get_detalle_by_hoja_id(hoja_de_ruta_id):
        """Retrieve detailed information for each Pedido in a Hoja de Ruta."""
        conn = HojaDeRutaPedido.get_db_connection()
        try:
            detalles = conn.execute('''
                SELECT * FROM hoja_de_ruta_detalle 
                WHERE hoja_de_ruta_id = ?
            ''', (hoja_de_ruta_id,)).fetchall()
            return detalles
        except sqlite3.Error as e:
            print(f"Error retrieving detailed hoja de ruta data: {e}")
        finally:
            HojaDeRutaPedido.close_connection(conn)
        return []
    
    
