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

PROGRESS_FILE = 'd:/YOP/BioAgent/progreso_transcripcion.json'
LINKS_FILE = 'd:/YOP/BioAgent/enlaces_extraidos.txt'
OUTPUT_DIR = 'd:/YOP/BioAgent/transcripciones'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_progress(progress):
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

def get_video_id(url):
    if 'youtu.be/' in url:
        return url.split('youtu.be/')[1].split('?')[0]
    elif 'v=' in url:
        return url.split('v=')[1].split('&')[0]
    return url.replace('/', '_').replace(':', '_')

def get_video_title(url):
    print(f"Obteniendo título para: {url}")
    command = ["uv", "run", "--with", "yt-dlp", "yt-dlp", "--get-title", url]
    try:
        res = subprocess.run(command, check=True, capture_output=True, text=True)
        return res.stdout.strip()
    except:
        return f"Video_{get_video_id(url)}"

def upload_to_tmpfiles(filepath):
    print(f"Hospedando temporalmente en tmpfiles.org: {filepath}")
    try:
        with open(filepath, 'rb') as f:
            r = requests.post('https://tmpfiles.org/api/v1/upload', files={'file': f})
            if r.status_code == 200:
                url = r.json().get('data', {}).get('url', '')
                return url.replace('tmpfiles.org/', 'tmpfiles.org/dl/')
            else:
                print(f"Error tmpfiles Status {r.status_code}: {r.text}")
    except Exception as e:
        print(f"Error tmpfiles Exception: {e}")
    return None

def download_audio(url, output_path):
    print(f"Descargando audio yt-dlp: {url}")
    command = [
        "uv", "run", "--with", "yt-dlp", "yt-dlp",
        "-f", "bestaudio/best",
        "-o", output_path,
        url
    ]
    try:
        subprocess.run(command, check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"Error descarga: {e}")
        return False

def fireflies_upload(url, title):
    print(f"Enviando a Fireflies: {title}")
    query = """
    mutation($input: AudioUploadInput!) {
        uploadAudio(input: $input) {
            success
            title
            message
        }
    }
    """
    variables = {"input": {"url": url, "title": title}}
    try:
        r = requests.post(GRAPHQL_URL, headers=HEADERS_GRAPHQL, json={"query": query, "variables": variables})
        return r.json()
    except Exception as e:
        print(f"Error Fireflies Upload Request: {e}")
        return None

def get_transcript(title):
    query = """
    query {
        transcripts {
            id
            title
            sentences {
                text
            }
        }
    }
    """
    try:
        r = requests.post(GRAPHQL_URL, headers=HEADERS_GRAPHQL, json={"query": query})
        data = r.json()
        if "data" in data and "transcripts" in data["data"]:
            for t in data["data"]["transcripts"]:
                if t["title"] == title:
                    return t
    except:
        pass
    return None

def main():
    progress = load_progress()
    with open(LINKS_FILE, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    print(f"Procesando {len(urls)} videos...")

    for i, url in enumerate(urls):
        vid = get_video_id(url)
        if vid in progress and progress[vid].get('status') == 'Completed':
            print(f"[{i+1}/{len(urls)}] Ya completado: {vid}")
            continue

        print(f"\n--- [{i+1}/{len(urls)}] Procesando: {url} ---")
        title = get_video_title(url)
        safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '_', '-')]).strip()
        ff_title = f"{vid}_{safe_title}"[:100]

        # 1. Descargar
        audio_file = f"d:/YOP/BioAgent/tmp_{vid}.m4a"
        if not os.path.exists(audio_file):
            if not download_audio(url, audio_file):
                continue

        # 2. Hostear
        direct_url = upload_to_tmpfiles(audio_file)
        if not direct_url:
            if os.path.exists(audio_file): os.remove(audio_file)
            continue

        # 3. Fireflies
        res = fireflies_upload(direct_url, ff_title)
        if os.path.exists(audio_file): os.remove(audio_file)

        if res:
            success_data = res.get('data', {})
            if success_data:
                upload_res = success_data.get('uploadAudio', {})
                if upload_res and upload_res.get('success'):
                    print("Subida a Fireflies exitosa. Esperando transcripción...")
                    progress[vid] = {'title': title, 'status': 'Processing', 'ff_title': ff_title}
                    save_progress(progress)

                    # Polling (hasta 15 minutos por video)
                    completed = False
                    for attempt in range(45): # 45 * 20s = 15m
                        time.sleep(20)
                        t_data = get_transcript(ff_title)
                        if t_data and t_data.get('sentences'):
                            # Guardar resultado
                            output_file = os.path.join(OUTPUT_DIR, f"{vid}.txt")
                            text = " ".join([s.get('text', '') for s in t_data['sentences']])
                            with open(output_file, 'w', encoding='utf-8') as out:
                                out.write(f"Título: {title}\nURL: {url}\n\n{text}")
                            
                            progress[vid]['status'] = 'Completed'
                            save_progress(progress)
                            print(f"¡Completado! Guardado en {output_file}")
                            completed = True
                            break
                        else:
                            print(f"  ...esperando ({attempt+1}/45)")
                    
                    if not completed:
                        print("Tiempo de espera agotado para este video.")
                else:
                    print(f"Fallo en Fireflies (uploadAudio): {upload_res}")
            else:
                print(f"Errores en Fireflies (data is null): {res.get('errors')}")
        else:
            print("Error: No se recibió respuesta de Fireflies.")

    print("\nProcesamiento terminado.")

if __name__ == "__main__":
    main()
