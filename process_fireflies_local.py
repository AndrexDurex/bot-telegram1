import os
import time
import requests
import json
import subprocess
from dotenv import load_dotenv

# Cargar variables de entorno (Fireflies API Key)
load_dotenv('d:/YOP/BioAgent/.env')
FIREFLIES_API_KEY = os.getenv('FIREFLIES_API_KEY')

if not FIREFLIES_API_KEY:
    print("Error: FIREFLIES_API_KEY no encontrada en d:/YOP/BioAgent/.env")
    exit(1)

HEADERS_GRAPHQL = {
    "Authorization": f"Bearer {FIREFLIES_API_KEY}",
    "Content-Type": "application/json"
}
# La subida de archivos requiere otro formato, sin application/json forzado para formData.
HEADERS_UPLOAD = {
    "Authorization": f"Bearer {FIREFLIES_API_KEY}"
}

GRAPHQL_URL = "https://api.fireflies.ai/graphql"

def download_audio(url, output_filename):
    """Descarga el audio de un video de YouTube usando yt-dlp."""
    print(f"Descargando audio de: {url}")
    # Formato m4a o mp3 suele ser suficientemente bueno y ligero.
    command = [
        "uv", "run", "--with", "yt-dlp", "yt-dlp",
        "-f", "ba",
        "-o", output_filename,
        url
    ]
    try:
        subprocess.run(command, check=True, capture_output=True)
        print(f"Audio descargado exitosamente: {output_filename}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error descargando el audio: {e.stderr.decode('utf-8')}")
        return False

def upload_audio_file(filepath, title):
    print(f"Subiendo {filepath} a Fireflies (v2REST)...")
    
    upload_url = "https://api.fireflies.ai/v2/upload"
    
    try:
        with open(filepath, 'rb') as f:
            files = {
                'file': (os.path.basename(filepath), f, 'audio/m4a')
            }
            data = {
                'title': title
            }
            response = requests.post(
                upload_url,
                headers=HEADERS_UPLOAD,
                files=files,
                data=data
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
    
    # Tomaremos el primer video como prueba de fuego
    test_url = urls[0]
    video_id = test_url.split('/')[-1].split('?')[0].replace('watch?v=', '')
    output_filename = f"{video_id}.m4a"
    title = f"NotebookLM_Source_{video_id}"
    
    # 1. Descargar audio
    if not download_audio(test_url, output_filename):
        return
        
    # 2. Subir audio
    upload_result = upload_audio_file(output_filename, title)
    print("Resultado Upload:", json.dumps(upload_result, indent=2))
    
    if upload_result and upload_result.get("data", {}).get("uploadAudio", {}).get("success"):
        returned_title = upload_result["data"]["uploadAudio"]["title"]
        print(f"Esperando transcripción para '{returned_title}'...")
        
        # 3. Polling (Max 10 minutos = 30 * 20s)
        for _ in range(30):
            time.sleep(20)
            transcript_data = get_transcript(returned_title)
            
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
    else:
        print("Fallo al subir el audio.")
        
    # 4. Limpiar archivo temporal
    if os.path.exists(output_filename):
        os.remove(output_filename)
        print(f"Archivo temporal {output_filename} eliminado.")

if __name__ == "__main__":
    process_links()
