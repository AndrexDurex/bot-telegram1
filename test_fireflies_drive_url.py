import os
import requests
import json
from dotenv import load_dotenv

load_dotenv('d:/YOP/BioAgent/.env')
FIREFLIES_API_KEY = os.getenv('FIREFLIES_API_KEY')

HEADERS_GRAPHQL = {
    "Authorization": f"Bearer {FIREFLIES_API_KEY}",
    "Content-Type": "application/json"
}

GRAPHQL_URL = "https://api.fireflies.ai/graphql"

def upload_audio_by_url(url, title):
    print(f"Subiendo a Fireflies usando URL pública de Drive...")
    
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

if __name__ == "__main__":
    file_id = "1bWYGWAp558tDzHkG6Md0gkHMkf2LqaSG"
    direct_download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    print(f"URL de descarga directa: {direct_download_url}")
    
    result = upload_audio_by_url(direct_download_url, "Test_Google_Drive_Upload")
    print(json.dumps(result, indent=2))
