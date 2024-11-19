import requests


"EAAIVU1arLZBwBOxVdMCIjSPNO03oYnpse5uEtOtZCNHYQZAucpCI45syyIc1jcybSApXUf01t59LCRAyZChHo2o2nsdNUBj4mAXD1CpovFK1eiHT3ZA3c6Rsiaox8XKZAaHZAnSxTSWmCOGU093YL5JfF09ZBzdQlWEMHTZAmNMSa3jvs6cmc1EmDDLtZAHLZAZC7F1n7Pi4fXt5vUXS2mftizsw6aJB63vMalmFAq9redgx2YcPj5SBBmwZD",
"506460215876483"
phone_number_id ="506460215876483"
headers = {
            'Authorization': 'Bearer EAAIVU1arLZBwBOxVdMCIjSPNO03oYnpse5uEtOtZCNHYQZAucpCI45syyIc1jcybSApXUf01t59LCRAyZChHo2o2nsdNUBj4mAXD1CpovFK1eiHT3ZA3c6Rsiaox8XKZAaHZAnSxTSWmCOGU093YL5JfF09ZBzdQlWEMHTZAmNMSa3jvs6cmc1EmDDLtZAHLZAZC7F1n7Pi4fXt5vUXS2mftizsw6aJB63vMalmFAq9redgx2YcPj5SBBmwZD',
            'Content-Type': 'application/json'}

url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"
data = { "messaging_product": "whatsapp"
        , "to": "541161236044",
          "type": "template", "template": { "name": "saludo", "language": { "code": "es_AR" } } }
response = requests.post(url, headers=headers, json=data)
for x in response:
    print(x)