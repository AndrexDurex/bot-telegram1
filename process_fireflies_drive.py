import os
import time
import requests
import json
import subprocess
from dotenv import load_dotenv

load_dotenv('d:/YOP/BioAgent/.env')
FIREFLIES_API_KEY = os.getenv('FIREFLIES_API_KEY')

HEADERS_GRAPHQL = {
    "Authorization": f"Bearer {FIREFLIES_API_KEY}",
    "Content-Type": "application/json"
}
GRAPHQL_URL = "https://api.fireflies.ai/graphql"

def get_google_drive_token():
    # Helper to get the token directly from mcp_config.json 
    config_path = r"C:\Users\aldri\.gemini\antigravity\mcp_config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('mcpServers', {}).get('googledrive', {}).get('env', {}).get('GOOGLE_ACCESS_TOKEN')
    except Exception as e:
        print(f"Error cargando config MCP: {e}")
        return None

def upload_to_drive(filepath, title):
    print(f"Subiendo {filepath} a Google Drive...")
    token = get_google_drive_token()
    if not token:
        print("No se encontró GOOGLE_ACCESS_TOKEN")
        return None

    # POST to Drive API
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    metadata = {
        'name': title,
        'mimeType': 'audio/m4a'
    }
    
    files = {
        'data': ('metadata', json.dumps(metadata), 'application/json; charset=UTF-8'),
        'file': (filepath, open(filepath, 'rb'), 'audio/m4a')
    }
    
    try:
        # Simple upload uri
        r = requests.post(
            "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
            headers=headers,
            files=files
        )
        if r.status_code == 200:
            file_id = r.json().get('id')
            print(f"Subido a Google Drive con ID: {file_id}")
            
            # Hacer el script publico para que Fireflies lo lea
            requests.post(
                f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions",
                headers=headers,
                json={"role": "reader", "type": "anyone"}
            )
            
            # Generar URL de descarga directa
            web_content_link = f"https://drive.google.com/uc?export=download&id={file_id}"
            return file_id, web_content_link
        else:
            print(f"Error subiendo a Drive: {r.text}")
            return None, None
    except Exception as e:
        print(f"Exception upload Drive: {e}")
        return None, None

def delete_from_drive(file_id):
    token = get_google_drive_token()
    print(f"Eliminando {file_id} de Google Drive...")
    requests.delete(
        f"https://www.googleapis.com/drive/v3/files/{file_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

def download_audio(url, output_filename):
    print(f"Descargando audio yt-dlp: {url}")
    command = [
        "uv", "run", "--with", "yt-dlp", "yt-dlp",
        "-f", "bestaudio/best",
        "-o", output_filename,
        url
    ]
    try:
        subprocess.run(command, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error descargando el audio: {e.stderr.decode('utf-8')}")
        return False

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
        print(f"Error en GraphQL upload: {e}")
        return None

def process_links():
    try:
        with open('d:/YOP/BioAgent/enlaces_extraidos.txt', 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
    except Exception as e:
        return

    test_url = urls[0]
    video_id = test_url.split('/')[-1].split('?')[0].replace('watch?v=', '')
    output_filename = f"{video_id}.m4a"
    title = f"NotebookLM_Source_{video_id}"
    
    if not os.path.exists(output_filename):
        if not download_audio(test_url, output_filename):
            print("Fallo yt-dlp")
            return
            
    drive_id, public_url = upload_to_drive(output_filename, output_filename)
    if drive_id and public_url:
        print(f"Link público: {public_url}")
        
        upload_result = upload_audio_by_url(public_url, title)
        print("Resultado Upload Fireflies:", json.dumps(upload_result, indent=2))
        
        if upload_result and upload_result.get("data", {}).get("uploadAudio", {}).get("success"):
            print("Esperando transcripción (1 minuto)...")
            time.sleep(60)
            
        delete_from_drive(drive_id)

    if os.path.exists(output_filename):
        os.remove(output_filename)

process_links()
