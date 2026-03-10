import os
import requests
import json
from dotenv import load_dotenv

load_dotenv('d:/YOP/BioAgent/.env')
FIREFLIES_API_KEY = os.getenv('FIREFLIES_API_KEY')

query = """
{
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

res = requests.post(
    "https://api.fireflies.ai/graphql", 
    headers={"Authorization": f"Bearer {FIREFLIES_API_KEY}", "Content-Type": "application/json"},
    json={"query": query}
)

data = res.json()
t = data.get('data', {}).get('__type')
if t:
    for f in t.get('inputFields', []):
        type_info = f.get('type')
        tname = type_info.get('name')
        if not tname and type_info.get('ofType'):
            tname = type_info['ofType'].get('name')
            
        print(f"- {f['name']}: {tname} ({type_info['kind']})")
else:
    print("No type found.", data)
