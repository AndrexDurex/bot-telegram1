import os
import time
import requests
import json
import subprocess
from dotenv import load_dotenv

# Cargar variables de entorno (Fireflies API Key)
load_dotenv('d:/YOP/BioAgent/.env')
FIREFLIES_API_KEY = os.getenv('FIREFLIES_API_KEY')

HEADERS_GRAPHQL = {
    "Authorization": f"Bearer {FIREFLIES_API_KEY}",
    "Content-Type": "application/json"
}

GRAPHQL_URL = "https://api.fireflies.ai/graphql"

def upload_audio_by_url(url, title):
    print(f"Subiendo por URL: {url} a Fireflies...")
    
    query = """
    mutation($input: AudioUploadInput!) {
        uploadAudio(input: $input) {
            success
            title
            message
        }
    }
    """
    
    variables = {
        "input": {
            "url": url,
            "title": title
        }
    }

    try:
        response = requests.post(
            GRAPHQL_URL,
            headers=HEADERS_GRAPHQL,
            json={"query": query, "variables": variables}
        )
        return response.json()
    except Exception as e:
        print(f"Error en la subida: {e}")
        return None

def process_links():
    try:
        with open('d:/YOP/BioAgent/enlaces_extraidos.txt', 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error leyendo enlaces: {e}")
        return

    print(f"Comenzando procesamiento de {len(urls)} enlaces...")
    
    test_url = urls[0]
    video_id = test_url.split('/')[-1].split('?')[0].replace('watch?v=', '')
    title = f"NotebookLM_Source_{video_id}"
    
    # Fireflies is VERY strict about direct MP3/M4A links. 
    # YouTube links don't work reliably directly in the input url anymore (success true but no transcript).
    upload_result = upload_audio_by_url(test_url, title)
    print("Resultado Upload:", json.dumps(upload_result, indent=2))

if __name__ == "__main__":
    process_links()
