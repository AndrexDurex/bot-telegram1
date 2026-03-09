import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('d:/YOP/BioAgent/.env')
FIREFLIES_API_KEY = os.getenv('FIREFLIES_API_KEY')

HEADERS = {
    'Authorization': f'Bearer {FIREFLIES_API_KEY}',
    'Content-Type': 'application/json'
}

query = """
query {
  __type(name: "AudioUploadInput") {
    name
    inputFields {
      name
      type {
        name
        kind
        ofType {
          name
          kind
        }
      }
    }
  }
}
"""

res = requests.post('https://api.fireflies.ai/graphql', headers=HEADERS, json={'query': query})
print(json.dumps(res.json(), indent=2))
