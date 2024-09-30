import sqlite3
import requests

DATABASE = 'vita.db'

class Cliente:
    def __init__(self, nombre_completo, celular, direccion, id=None, estado_conversacion=None, producto_seleccionado=None):
        self.id = id
        self.nombre_completo = nombre_completo
        self.celular = celular
        self.direccion = direccion
        self.estado_conversacion = estado_conversacion
        self.producto_seleccionado = producto_seleccionado

    # Método para conectar a la base de datos
    @staticmethod
    def get_db_connection():
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row  # Permite acceder a los datos por nombre de columna
        return conn

    # Método para crear o actualizar un cliente en la base de datos
    def save(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()

        if self.id:  # Si ya tiene un ID, actualizamos el cliente
            cursor.execute('''
                UPDATE clientes
                SET nombre_completo = ?, celular = ?, direccion = ?, estado_conversacion = ?, producto_seleccionado = ?
                WHERE id = ?
            ''', (self.nombre_completo, self.celular, self.direccion, self.estado_conversacion, self.producto_seleccionado, self.id))
        else:  # Si no tiene ID, lo creamos
            cursor.execute('''
                INSERT INTO clientes (nombre_completo, celular, direccion, estado_conversacion, producto_seleccionado)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.nombre_completo, self.celular, self.direccion, self.estado_conversacion, self.producto_seleccionado))
            self.id = cursor.lastrowid  # Obtener el ID del cliente recién insertado

        conn.commit()
        conn.close()

    # Método para eliminar un cliente
    def delete(self):
        if self.id:
            conn = self.get_db_connection()
            conn.execute('DELETE FROM clientes WHERE id = ?', (self.id,))
            conn.commit()
            conn.close()

    # Método para obtener un cliente por ID
    @staticmethod
    def get_by_id(id):
        conn = Cliente.get_db_connection()
        cliente_row = conn.execute('SELECT * FROM clientes WHERE id = ?', (id,)).fetchone()
        conn.close()
        if cliente_row:
            return Cliente(cliente_row['nombre_completo'], cliente_row['celular'], cliente_row['direccion'],
                           cliente_row['id'], cliente_row['estado_conversacion'], cliente_row['producto_seleccionado'])
        return None

    # Método para obtener todos los clientes
    @staticmethod
    def get_all():
        conn = Cliente.get_db_connection()
        clientes = conn.execute('SELECT * FROM clientes').fetchall()
        conn.close()
        return [Cliente(cliente['nombre_completo'], cliente['celular'], cliente['direccion'], cliente['id'],
                        cliente['estado_conversacion'], cliente['producto_seleccionado']) for cliente in clientes]

    # Método para obtener un cliente por número de celular
    @staticmethod
    def obtener_por_celular(celular):
        conn = Cliente.get_db_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM clientes WHERE celular = ?"
        cursor.execute(query, (celular,))
        row = cursor.fetchone()
        conn.close()

        if row:
            # Retornar un objeto Cliente si se encuentra en la base de datos
            return Cliente(
                nombre_completo=row['nombre_completo'],
                celular=row['celular'],
                direccion=row['direccion'],
                id=row['id'],
                estado_conversacion=row['estado_conversacion'],
                producto_seleccionado=row['producto_seleccionado']
            )
        return None

class Producto:
    def __init__(self, nombre, descripcion, precio, id=None):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio

    # Método para conectar a la base de datos
    @staticmethod
    def get_db_connection():
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

    # Método para crear o actualizar un producto
    def save(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()

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
        conn.close()

    # Método para eliminar un producto
    def delete(self):
        if self.id:
            conn = self.get_db_connection()
            conn.execute('DELETE FROM productos WHERE id = ?', (self.id,))
            conn.commit()
            conn.close()

    # Método para obtener un producto por ID
    @staticmethod
    def get_by_id(id):
        conn = Producto.get_db_connection()
        producto_row = conn.execute('SELECT * FROM productos WHERE id = ?', (id,)).fetchone()
        conn.close()
        if producto_row:
            return Producto(producto_row['nombre'], producto_row['descripcion'], producto_row['precio'], producto_row['id'])
        return None
    
    @staticmethod
    def get_by_nombre(nombre):
        conn = Producto.get_db_connection()
        producto_row = conn.execute('SELECT * FROM productos WHERE nombre = ?', (nombre,)).fetchone()
        conn.close()
        if producto_row:
            return Producto(producto_row['nombre'], producto_row['descripcion'], producto_row['precio'], producto_row['id'])
        return None

    # Método para obtener todos los productos
    @staticmethod
    def get_all():
        conn = Producto.get_db_connection()
        productos = conn.execute('SELECT * FROM productos').fetchall()
        conn.close()
        return [Producto(producto['nombre'], producto['descripcion'], producto['precio'], producto['id']) for producto in productos]
    

class Pedido:
    def __init__(self, cliente_id, producto_id, cantidad, estado = None, id=None):
        self.id = id
        self.cliente_id = cliente_id
        self.producto_id = producto_id
        self.cantidad = cantidad
        self.estado = estado

    # Conexión a la base de datos
    @staticmethod
    def get_db_connection():
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

    # Guardar o actualizar un pedido
    def save(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()

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
        conn.close()

    # Eliminar un pedido
    def delete(self):
        if self.id:
            conn = self.get_db_connection()
            conn.execute('DELETE FROM pedidos WHERE id = ?', (self.id,))
            conn.commit()
            conn.close()

    # Obtener pedido por ID
    @staticmethod
    def get_by_id(id):
        conn = Pedido.get_db_connection()
        pedido_row = conn.execute('SELECT * FROM pedidos WHERE id = ?', (id,)).fetchone()
        conn.close()
        if pedido_row:
            return Pedido(pedido_row['cliente_id'], pedido_row['producto_id'], pedido_row['cantidad'], pedido_row['estado'], pedido_row['id'])
        return None

    
    # Obtener todos los pedidos
    @staticmethod
    def get_all():
        conn = Pedido.get_db_connection()
        pedidos = conn.execute('SELECT * FROM pedidos').fetchall()
        conn.close()
        return [Pedido(pedido['cliente_id'], pedido['producto_id'], pedido['cantidad'], pedido['estado'], pedido['id']) for pedido in pedidos]
    @staticmethod
    def get_vista():
        conn = Pedido.get_db_connection()
        pedidos = conn.execute("""
                               SELECT c.nombre_completo as nombre ,pro.nombre as producto,p.cantidad as cantidad,p.estado as estado,p.id as id,pro.precio * p.cantidad as total
                               FROM pedidos AS p
                               JOIN clientes AS c ON p.cliente_id = c.id
                               JOIN productos AS pro ON p.producto_id = pro.id
                               """
                               ).fetchall()
        conn.close()
        return pedidos
    

class WhatsAppBot:
    def __init__(self, api_key, phone_number_id):
        self.api_key = api_key
        self.phone_number_id = phone_number_id
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.Conversaciones=[]

    def enviar_mensaje(self, celular, mensaje):
        url = f"https://graph.facebook.com/v20.0/{self.phone_number_id}/messages"
        data = {
            "messaging_product": "whatsapp",
            "to": celular,
            "type": "text",
            "text": {
                "body": mensaje
            }
        }
        response = requests.post(url, headers=self.headers, json=data)
        conversacion = self.conversation_by_id(celular)
        if conversacion:
            conversacion.update_status()
        else:
            conversacion = Conversation(celular)
            conversacion.update_status()
            self.Conversaciones.append(conversacion)
            
        return response.json()
    
    def enviar_template(self,celular, template):
        url = f"https://graph.facebook.com/v20.0/{self.phone_number_id}/messages"
        data = {
            "messaging_product": "whatsapp",
            "to": celular,
            "type": "template",
            "template": {
                "name": template,
                "language":{
                    "code": "es_AR"
                }
            }
        }
        response = requests.post(url, headers=self.headers, json=data)
        conversacion = self.conversation_by_id(celular)
        if conversacion:
            if conversacion.status != 0:
                return ValueError
            conversacion.update_status()
            print(conversacion.status)
        else:
            conversacion = Conversation(celular)
            conversacion.update_status()
            self.Conversaciones.append(conversacion)
            print(conversacion.status)
            
        return response.json()        

    def parse_number(self,number):
        if number[:3] == "549":
            test = number[:2]
            aux = number[3:]
            number=test + aux
        return number

    def enviar_mensaje_masivo(self, clientes, mensaje):
        for cliente in clientes:
            self.enviar_mensaje(cliente[1], mensaje)  # Suponemos que cliente[1] es el celular

    def conversation_by_id(self,id):
        if len(self.Conversaciones) == 0:
            return False
        for x in self.Conversaciones:
            if x.phone == id:
                return x
            else:
                return False
        

    def procesar_mensaje(self, data):
        #Validar que sea un mensaje
        if 'messages' in data['entry'][0]['changes'][0]['value']:
            message_data = data['entry'][0]['changes'][0]['value']['messages'][0]    
            #Revisar si hay una conversacion activa para ese numero
            phone_number = self.parse_number(message_data['from'])
            print(data)
            conversation = self.conversation_by_id(phone_number)
            if conversation != False:
                conversation.nuevo_mensaje(message_data)
            else:
                self.Conversaciones.append(Conversation(phone_number))
                conversation = self.Conversaciones[-1]
                conversation.nuevo_mensaje(message_data)
            
            if conversation.get_status() == 1:
                print(conversation.get_ultimo_mensaje().text)
                conversation.producto = conversation.get_ultimo_mensaje().text
                self.enviar_mensaje(phone_number,"¿Cuantos van a necesitar?")
            if conversation.get_status() == 2:
                pass

        return False


    def confirmar_pedido(self, cliente, productos):
        # Confirma y guarda el pedido del cliente
        pedido = Pedido(cliente['celular'], productos)
        pedido.guardar()
        return "Tu pedido ha sido confirmado."

class Conversation:
    def __init__(self, phone):
       self.Mensajes = [Mensaje]
       self.phone = phone
       self.status = 0
       self.producto =""
       self.cantidad =0

    def nuevo_mensaje(self,data):
        self.Mensajes.append(Mensaje(data))

    def get_ultimo_mensaje(self):
        return self.Mensajes[-1]
    
    def update_status(self):
        self.status = self.status + 1
        print(self.status)
    def get_status(self):
        return self.status

class Mensaje:
    def __init__(self, data):
        self.data = data
        self.text = ""
        self.parse_text(data)

    def parse_text(self,data):
        if data['type'] == 'interactive' and data['interactive']['type'] == 'button_reply':
            text = data['interactive']['button_reply']['title']
        elif data['type'] == 'button':
            text = str(data['button']['text'])
        else:
            text = data['text']['body']  # Texto del mensaje

        self.text = text
    
    def get_text(self):
        return self.text

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
    def __init__(self):
        self.ACCESS_TOKEN = ""
        pass

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

    def enviar_mensaje(self, mensaje):
        # Función para interactuar con la API de WhatsApp
        url = 'https://graph.facebook.com/v20.0/364603270066493/messages'
        headers = {
            'Authorization': f'Bearer {self.ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, json=mensaje)
        if response.status_code == 200:
            print(f"Mensaje enviado a {mensaje['to']}")
        else:
            print(f"Error al enviar mensaje: {response.text}")

    def procesar_mensaje(self, data):
        # Procesar la respuesta del cliente
        print(data)
        if 'messages' in data['entry'][0]['changes'][0]['value']:
            message_data = data['entry'][0]['changes'][0]['value']['messages'][0]
            cliente_celular = self.parse_number(message_data['from'])
            texto_mensaje = self.parse_text(message_data)

            # Buscar cliente por su número de celular
            cliente = Cliente.obtener_por_celular(cliente_celular)
            print(texto_mensaje)
            if cliente:
                if cliente.estado_conversacion == "esperando_producto":
                    self.preguntar_cantidad(cliente, texto_mensaje)
                elif cliente.estado_conversacion == "esperando_cantidad":
                    self.confirmar_pedido(cliente, texto_mensaje)

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
        self.enviar_mensaje(mensaje)

        # Resetear el estado de la conversación del cliente
        cliente.estado_conversacion = None
        cliente.producto_seleccionado = None
        cliente.save()
