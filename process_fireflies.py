import os
import time
import requests
import json
from dotenv import load_dotenv

# Cargar variables de entorno (Fireflies API Key)
load_dotenv('d:/YOP/BioAgent/.env')
FIREFLIES_API_KEY = os.getenv('FIREFLIES_API_KEY')

if not FIREFLIES_API_KEY:
    print("Error: FIREFLIES_API_KEY no encontrada en d:/YOP/BioAgent/.env")
    exit(1)

HEADERS = {
    "Authorization": f"Bearer {FIREFLIES_API_KEY}",
    "Content-Type": "application/json"
}

GRAPHQL_URL = "https://api.fireflies.ai/graphql"

def upload_audio_url(audio_url):
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
            "url": audio_url,
            "title": f"NotebookLM_Source_{audio_url.split('/')[-1].split('?')[0]}"
        }
    }
    
    response = requests.post(
        GRAPHQL_URL,
        headers=HEADERS,
        json={"query": query, "variables": variables}
    )
    
    return response.json()

def get_all_transcripts():
    query = """
    query {
        transcripts {
            id
            title
            status
        }
    }
    """
    
    response = requests.post(GRAPHQL_URL, headers=HEADERS, json={"query": query})
def get_transcript(title):
    query = """
    query {
        transcripts {
            id
            title
            sentences {
                text
            }
            status
        }
    }
    """
    
    response = requests.post(GRAPHQL_URL, headers=HEADERS, json={"query": query})
    data = response.json()
    
    if "data" in data and "transcripts" in data["data"]:
        for t in data["data"]["transcripts"]:
            if t["title"] == title:
                return t
    return None

def process_links():
    print("Obteniendo lista actual de transcripciones desde Fireflies...")
    data = get_all_transcripts()
    # Mostrar todas las que están completadas
    if isinstance(data, dict) and "data" in data and "transcripts" in data["data"]:
        for t in data["data"]["transcripts"]:
            print(f"- {t.get('title')}: {t.get('status')}")
    else:
        print("Respuesta no esperada de Fireflies:")
        print(json.dumps(data, indent=2))

    # Cargar enlaces
    try:
        with open('d:/YOP/BioAgent/enlaces_extraidos.txt', 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error leyendo enlaces: {e}")
        return

    print(f"\nComenzando procesamiento de {len(urls)} enlaces...")
    
    # Procesaremos solo el primero como prueba inicial
    test_url = urls[0]
    print(f"Subiendo: {test_url}")
    
    upload_result = upload_audio_url(test_url)
    print("Resultado Upload:", json.dumps(upload_result, indent=2))
    
    if upload_result.get("data", {}).get("uploadAudio", {}).get("success"):
        title = upload_result["data"]["uploadAudio"]["title"]
        print(f"Esperando transcripción para '{title}'...")
        
        # Polling (Max 5 minutos = 30 * 10s)
        for _ in range(30):
            time.sleep(10)
            transcript_data = get_transcript(title)
            
            if transcript_data:
                status = transcript_data.get("status")
                print(f"Estado actual: {status}")
                
                if status == "Completed":
                    sentences = transcript_data.get("sentences", [])
                    full_text = " ".join([s.get("text", "") for s in sentences if s.get("text")])
                    print("\n¡Transcripción Completada!\n")
                    print(full_text[:500] + "...\n")
                    return
            else:
                print("Aún no aparece en la lista...")
                
        print("Timeout esperado por transcripción.")
    else:
        print("Fallo al subir el audio.")

if __name__ == "__main__":
    process_links()
