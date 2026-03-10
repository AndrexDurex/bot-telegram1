import os
import requests
import json
from dotenv import load_dotenv

load_dotenv('d:/YOP/BioAgent/.env')
FIREFLIES_API_KEY = os.getenv('FIREFLIES_API_KEY')

HEADERS = {
    'Authorization': f'Bearer {FIREFLIES_API_KEY}'
}

# Creemos un archivo minusculo dummy de audio MP3 para saltar el limite de 413 
# y ver si el problema es de sintaxis multipart o limitacion pura de tamaño
dummy_file = 'd:/YOP/BioAgent/dummy.mp3'
with open(dummy_file, 'wb') as f:
    f.write(os.urandom(1024 * 50)) # 50KB dummy file

with open(dummy_file, 'rb') as f:
    operations = json.dumps({
        "query": "mutation($file: Upload!, $title: String) { uploadAudio(input: { file: $file, title: $title }) { success message title } }",
        "variables": {
            "file": None,
            "title": "Prueba Mini"
        }
    })
    
    map_data = json.dumps({
        "0": ["variables.file"]
    })
    
    files = {
        'operations': (None, operations),
        'map': (None, map_data),
        '0': ('dummy.mp3', f, 'audio/mpeg')
    }
    
    res = requests.post(
        'https://api.fireflies.ai/graphql',
        headers=HEADERS,
        files=files
    )

print("Status Code:", res.status_code)
print("Response:", res.text)
