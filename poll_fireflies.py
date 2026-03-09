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

if __name__ == "__main__":
    title_to_check = "Test_Google_Drive_Upload"
    print(f"Checking for transcript: '{title_to_check}'")
    
    for i in range(10):
        print(f"Intento {i+1}...")
        t = get_transcript(title_to_check)
        if t:
            print(f"Status: {t.get('status')}")
            if t.get('status') == 'Completed':
                sentences = t.get('sentences', [])
                if sentences:
                    print("Texto:")
                    print(sentences[0].get('text', 'No text in sentence 0...'))
                break
        else:
            print("Not found yet.")
            
        time.sleep(10)
    print("Done polling.")
