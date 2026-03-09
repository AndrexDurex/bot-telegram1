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

def get_direct_audio_url(youtube_url):
    print(f"Extrayendo URL directa de audio para: {youtube_url}")
    command = [
        "uv", "run", "--with", "yt-dlp", "yt-dlp",
        "-f", "bestaudio/best",
        "-g", # -g is for --get-url
        youtube_url
    ]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        # yt-dlp puede imprimir validaciones que no son URLs completas o avisos. 
        # Tomar la primera linea de stdout que empiece con http
        direct_url = next((line for line in result.stdout.split('\n') if line.startswith('http')), None)
        if direct_url:
            print(f"URL directa obtenida (longitud {len(direct_url)} chars)")
            return direct_url
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error extrayendo URL: {e.stderr}")
        return None

def upload_audio_by_url(url, title):
    print(f"Subiendo a Fireflies usando direct media URL...")
    
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

def get_transcript(title):
    query = """
    query {
        transcripts {
            id
            title
            status
            sentences {
                raw_text
                text
            }
        }
    }
    """
    
    response = requests.post(GRAPHQL_URL, headers=HEADERS_GRAPHQL, json={"query": query})
    data = response.json()
    
    if "data" in data and "transcripts" in data["data"]:
        for t in data["data"]["transcripts"]:
            if t["title"] == title:
                return t
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
    
    # Obtener el verdadero source raw media URL (googlevideo.com/...)
    direct_media_url = get_direct_audio_url(test_url)
    
    if not direct_media_url:
        print("Fallo al obtener la URL directa.")
        return
        
    upload_result = upload_audio_by_url(direct_media_url, title)
    print("Resultado Upload:", json.dumps(upload_result, indent=2))
    
    if upload_result and upload_result.get("data", {}).get("uploadAudio", {}).get("success"):
        print(f"Esperando transcripción para '{title}'...")
        
        # Polling (Max 10 minutos)
        for _ in range(30):
            time.sleep(20)
            transcript_data = get_transcript(title)
            
            if transcript_data:
                status = transcript_data.get("status")
                print(f"Estado actual: {status}")
                
                if status == "Completed":
                    sentences = transcript_data.get("sentences", [])
                    full_text = " ".join([s.get("text", "") for s in sentences if s.get("text")])
                    print("\n¡Transcripción Completada!\n")
                    print(full_text[:500] + "...\n")
                    break
            else:
                print("Aún no aparece en la lista...")
                
        print("Fin de ciclo para video 1.")

if __name__ == "__main__":
    process_links()
