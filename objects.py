import datetime
import csv
# Clase para un mensaje
class Message:
    def __init__(self, message_id, sender, text):
        self.message_id = message_id
        self.sender = sender
        self.text = text
        self.timestamp = datetime.datetime.now()
        self.sent = False       # Estado: enviado
        self.delivered = False  # Estado: entregado
        self.read = False       # Estado: leído

    def update_status(self, status):
        if status == "sent":
            self.sent = True
        elif status == "delivered":
            self.delivered = True
        elif status == "read":
            self.read = True
# Clase para una conversación
class Conversation:
    def __init__(self, customer_id):
        self.customer_id = customer_id
        self.messages = []
        self.status = 0
        self.product : str
        self.quantity : int

    def add_message(self, message):
        self.messages.append(message)

    def get_message_by_id(self, message_id):
        for message in self.messages:
            if message.message_id == message_id:
                return message
        return None

    def get_last_message(self):
        return self.messages[-1] if self.messages else None
    
    def upgrade_status(self):
        self.status += 1
    def get_status(self):
        return self.status

    def save_order(self):
        if self.product and self.quantity:
            data ={
                'numero' : self.customer_id,
                'producto' : self.product,
                'cantidad' : self.quantity
            }
            with open('pedidos.csv', 'w', newline='') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
                spamwriter.writerow([self.customer_id,self.product,self.quantity])

