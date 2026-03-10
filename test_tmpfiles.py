import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv('d:/YOP/BioAgent/.env')
FIREFLIES_API_KEY = os.getenv('FIREFLIES_API_KEY')

HEADERS_GRAPHQL = {
    "Authorization": f"Bearer {FIREFLIES_API_KEY}",
    "Content-Type": "application/json"
}

GRAPHQL_URL = "https://api.fireflies.ai/graphql"

def upload_to_tmpfiles(filepath):
    print(f"Subiendo {filepath} a tmpfiles.org...")
    try:
        with open(filepath, 'rb') as f:
            files = {'file': f}
            response = requests.post('https://tmpfiles.org/api/v1/upload', files=files)
            
            if response.status_code == 200:
                # The response URL is like https://tmpfiles.org/12345/file.m4a
                # The direct download URL is https://tmpfiles.org/dl/12345/file.m4a
                data = response.json()
                uploaded_url = data.get('data', {}).get('url', '')
                direct_url = uploaded_url.replace('tmpfiles.org/', 'tmpfiles.org/dl/')
                print(f"Subida exitosa. Direct URL: {direct_url}")
                return direct_url
            else:
                print(f"Error subiendo: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"Exception subiendo a tmpfiles: {e}")
        return None

def upload_audio_by_url(url, title):
    print(f"Enviando {url} a Fireflies...")
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
        res = requests.post(
            GRAPHQL_URL,
            headers=HEADERS_GRAPHQL,
            json={"query": query, "variables": variables}
        )
        return res.json()
    except Exception as e:
        print(f"Error GraphQL upload: {e}")
        return None

if __name__ == "__main__":
    filepath = "d:/YOP/BioAgent/5omDnw90dVo.m4a"
    title = "Test_TmpFiles_Upload"
    
    direct_url = upload_to_tmpfiles(filepath)
    if direct_url:
        result = upload_audio_by_url(direct_url, title)
        print("Resultado Fireflies:", json.dumps(result, indent=2))
        
        # Fireflies might take a second to queue
        time.sleep(2)
