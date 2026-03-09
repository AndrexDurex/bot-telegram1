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

def check_recent_transcripts():
    query = """
    query {
        transcripts {
            id
            title
            date
        }
    }
    """
    
    response = requests.post(GRAPHQL_URL, headers=HEADERS_GRAPHQL, json={"query": query})
    data = response.json()
    
    if "data" in data and "transcripts" in data["data"]:
        transcripts = data["data"]["transcripts"]
        print(f"Top 5 transcripciones recientes de {len(transcripts)} totales:")
        for t in transcripts[:5]:
            print(f"- [{t.get('date')}] ID: {t.get('id')} | Título: {t.get('title')}")
    else:
        print("No se pudieron obtener las transcripciones:", json.dumps(data, indent=2))

if __name__ == "__main__":
    check_recent_transcripts()
