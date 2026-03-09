import os
import time
import requests
import json
from dotenv import load_dotenv

load_dotenv('d:/YOP/BioAgent/.env')
FIREFLIES_API_KEY = os.getenv('FIREFLIES_API_KEY')

HEADERS = {
    'Authorization': f'Bearer {FIREFLIES_API_KEY}'
}

file_path = 'd:/YOP/BioAgent/5omDnw90dVo.m4a'
with open(file_path, 'rb') as f:
    
    # Payload format according to GraphQL multipart request spec
    operations = json.dumps({
        "query": "mutation($file: Upload!, $title: String) { uploadAudio(input: { file: $file, title: $title }) { success message title } }",
        "variables": {
            "file": None,
            "title": "REST_TEST"
        }
    })
    
    map_data = json.dumps({
        "0": ["variables.file"]
    })
    
    files = {
        'operations': (None, operations),
        'map': (None, map_data),
        '0': ('5omDnw90dVo.m4a', f, 'audio/m4a')
    }
    
    try:
        res = requests.post(
            'https://api.fireflies.ai/graphql',
            headers=HEADERS,
            files=files
        )
        print("Status Code:", res.status_code)
        print("Response:", res.text)
    except Exception as e:
        print("Error during upload:", e)
