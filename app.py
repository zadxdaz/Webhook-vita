from flask import Flask, request, jsonify
import requests
from objects import *

conversations = {}
ACCESS_TOKEN = "EAA0yrfyTgOgBO1H9iuxju8z5JRUkumSoeQxZCy8ByTYaQHZBAQbSAXb1vrLIDrmhqC1s7zw8cDKIfiZBuOpPR76038WZCbmHSZAZBl0tDvZCDpZAlN8W2IjObISIkc8CgyyCsQ6OEZBN50BDLnSpgGf0F3MmdjhlXzqgsedisCqZCPUpWqZCe8gpZAtVVGZAH2oo6IWlcZCtmkbrpOFKBt0xNoWCiXCUtrmbXIHCGvDmXl"
API_URL =  "https://graph.facebook.com/v20.0/364603270066493/messages"

productos =['Bidón de 12 Litros','Bidón de 20 Litros']
def parse_number(number):
    if number[:3] == "549":
        test = number[:2]
        aux = number[3:]
        number=test + aux
    return number

def send_template_message(recipient,template_name):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": parse_number(recipient),
        "type": "template",
        "template": {"name": template_name,
        'language':{'code':'es_AR'}}
    }
    response = requests.post(API_URL, headers=headers, json=data)
    if response.status_code == 200:
        print("Mensaje enviado con éxito")
    else:
        print(f"Error al enviar el mensaje: {response.status_code}, {response.text}")

def send_whatsapp_message(phone_number, message):
    url = "https://graph.facebook.com/v20.0/364603270066493/messages"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": parse_number(phone_number),
        "type": "text",
        "text": {"body": message}
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Mensaje enviado con éxito")
    else:
        print(f"Error al enviar el mensaje: {response.status_code}, {response.text}")


def send_interactive_message(recipient_id, message_body):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": message_body
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "12_liters",
                            "title": "Bidón de 12 litros"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "20_liters",
                            "title": "Bidón de 20 litros"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "soda",
                            "title": "Cajon de soda"
                        }
                    }
                ]
            }
        }
    }

    response = requests.post(API_URL, json=data, headers=headers)
    return response.json()
# Enviar el mensaje para seleccionar el producto
def send_product_selection_message(phone_number):
    message_body = "Por favor, seleccioná el tipo de bidón:"
    return send_interactive_message(phone_number, message_body)
# Enviar el mensaje para seleccionar la cantidad
def send_quantity_selection_message(phone_number):
    message_body = "¿Cuántos bidones necesitás?"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": message_body
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "quantity_1",
                            "title": "1"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "quantity_2",
                            "title": "2"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "quantity_3",
                            "title": "3"
                        }
                    }
                ]
            }
        }
    }

    response = requests.post(API_URL, json=data, headers=headers)
    return response.json()
# Función para procesar los mensajes y tomar decisiones
def process_message(conversation:Conversation):
    last_message = conversation.get_last_message()
    phases = ["introduccion","consulta","validacion","confirmado"]

    if conversation.get_status() == 0 and conversation.get_last_message().text:
        send_template_message(conversation.customer_id,'saludo')
        conversation.upgrade_status()
        print(conversation.status)
    if conversation.get_status() == 1 and conversation.get_last_message().text in productos:
        conversation.product = last_message.text
        send_quantity_selection_message(parse_number(conversation.customer_id))
        conversation.upgrade_status()
    if conversation.get_status() == 2:
        if last_message.text.isnumeric():
            conversation.quantity = int(last_message.text)
            cantida = conversation.quantity
            producto = conversation.product
            text = f"Se registro su pedido de {cantida} {producto}"
            send_whatsapp_message(parse_number(conversation.customer_id),text)
            conversation.save_order()
            conversation.upgrade_status()




app = Flask(__name__)

WEBHOOK_VERIFY_TOKEN = "ASLDNKFUIOQWHBDFA213fa"


# Ruta para manejar los mensajes entrantes y actualizar el estado de los mensajes
@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    data = request.get_json()
    print(data)

    # Procesar nuevo mensaje
    if 'messages' in data['entry'][0]['changes'][0]['value']:
        message_data = data['entry'][0]['changes'][0]['value']['messages'][0]
        phone_number = message_data['from']  # Número del cliente
        message_id = message_data['id']  # ID único del mensaje
        
        if message_data['type'] == 'interactive' and message_data['interactive']['type'] == 'button_reply':
            text = message_data['interactive']['button_reply']['title']
        elif message_data['type'] == 'button':
            text = str(message_data['button']['text'])
        else:
            text = message_data['text']['body']  # Texto del mensaje

        # Si no existe una conversación para este cliente, la creamos
        if phone_number not in conversations:
            conversations[phone_number] = Conversation(phone_number)

        # Creamos un nuevo mensaje y lo agregamos a la conversación
        new_message = Message(message_id, phone_number, text)
        print(text)
        conversations[phone_number].add_message(new_message)

        # Tomar decisiones basadas en el contenido del mensaje
        process_message(conversations[phone_number])

    # Procesar actualización de estado del mensaje
    if 'statuses' in data['entry'][0]['changes'][0]['value']:
        status_data = data['entry'][0]['changes'][0]['value']['statuses'][0]
        message_id = status_data['id']  # ID del mensaje
        status = status_data['status']  # Estado: 'sent', 'delivered', 'read'
        phone_number = status_data['recipient_id']  # Número del cliente

        # Actualizamos el estado del mensaje correspondiente
        if phone_number in conversations:
            conversation = conversations[phone_number]
            message = conversation.get_message_by_id(message_id)
            if message:
                message.update_status(status)
                print(f"Mensaje {message_id} actualizado a {status}.")

    return jsonify({"status": "received"}), 200
# Ruta para verificar el webhook
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    # Obtiene los parámetros de la solicitud GET
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    # Verifica que el modo y el token son correctos
    if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN:
        # Responde con el challenge token para verificar el webhook
        return challenge, 200
    else:
        # Responde con 403 si el token no coincide
        return "Forbidden", 403

# Ruta principal opcional (opcional, como en el ejemplo original)
@app.route('/')
def index():
    return "<pre>Nothing to see here. Checkout README.md to start.</pre>"

@app.route("/test")
def test():
    return "<h1>Hola mundo</h1>"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
