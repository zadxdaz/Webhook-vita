import sqlite3
from objetos2 import Cliente  # Import the Cliente class
from objetos2 import Bot          # Import the WhatsApp Bot class for sending messages

DATABASE = 'vita.db'  # Path to your database

class ClientList:
    def __init__(self, list_id=None, name=None):
        self.list_id = list_id
        self.name = name

    # Method to create a new client list
    @staticmethod
    def create_list(name):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO client_lists (name) VALUES (?)', (name,))
        conn.commit()
        conn.close()

    # Method to add a client to a list
    @staticmethod
    def add_client_to_list(list_id, client_id):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO list_members (list_id, client_id) VALUES (?, ?)', (list_id, client_id))
        conn.commit()
        conn.close()

    # Method to remove a client from a list
    @staticmethod
    def remove_client_from_list(list_id, client_id):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM list_members WHERE list_id = ? AND client_id = ?', (list_id, client_id))
        conn.commit()
        conn.close()

    # Method to get all clients in the list as Cliente objects
    def get_clients(self):
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.* FROM clientes c
            JOIN list_members lm ON c.id = lm.client_id
            WHERE lm.list_id = ?
        ''', (self.list_id,))
        client_rows = cursor.fetchall()
        conn.close()

        # Return a list of Cliente objects
        return [Cliente(
                    id=row['id'],
                    nombre_completo=row['nombre_completo'],
                    celular=row['celular'],
                    direccion=row['direccion'],
                    estado_conversacion=row['estado_conversacion'],
                    producto_seleccionado=row['producto_seleccionado']
                ) for row in client_rows]

    # Method to send a WhatsApp message to all clients in the list
    def send_mass_message(self, message, bot_api_key, bot_phone_number_id):
        clients = self.get_clients()  # Get all clients in the list
        bot = Bot(api_key=bot_api_key, phone_number_id=bot_phone_number_id)

        for client in clients:
            bot.enviar_mensaje(client.celular, message)

    # Method to get a list by ID
    @staticmethod
    def get_list_by_id(list_id):
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM client_lists WHERE id = ?', (list_id,))
        list_row = cursor.fetchone()
        conn.close()

        if list_row:
            return ClientList(list_id=list_row['id'], name=list_row['name'])
        return None

    # Method to retrieve all client lists
    @staticmethod
    def get_all_lists():
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM client_lists')
        list_rows = cursor.fetchall()
        conn.close()

        return [ClientList(list_id=row['id'], name=row['name']) for row in list_rows]

    def delete(self):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Delete the list from the client_lists table
        cursor.execute('DELETE FROM client_lists WHERE id = ?', (self.list_id,))

        # Delete associated members from the list_members table
        cursor.execute('DELETE FROM list_members WHERE list_id = ?', (self.list_id,))

        conn.commit()
        conn.close()