import requests

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer EAAIVU1arLZBwBOxVdMCIjSPNO03oYnpse5uEtOtZCNHYQZAucpCI45syyIc1jcybSApXUf01t59LCRAyZChHo2o2nsdNUBj4mAXD1CpovFK1eiHT3ZA3c6Rsiaox8XKZAaHZAnSxTSWmCOGU093YL5JfF09ZBzdQlWEMHTZAmNMSa3jvs6cmc1EmDDLtZAHLZAZC7F1n7Pi4fXt5vUXS2mftizsw6aJB63vMalmFAq9redgx2YcPj5SBBmwZD',
}

json_data = {
    'messaging_product': 'whatsapp',
    'pin': '696969',
}

response = requests.post('https://graph.facebook.com/v20.0/506460215876483/register ', headers=headers, json=json_data)
for x in response:
    print(x)
# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '\n{\n  "messaging_product": "whatsapp",\n  "pin": "212834"\n} '
#response = requests.post('https://graph.facebook.com/v21.0/106540352242922/register ', headers=headers, data=data)