import json
import codecs

with codecs.open('d:/YOP/BioAgent/fireflies_schema.json', 'r', encoding='utf-16le') as f:
    try:
        data = json.load(f)
        found = False
        if 'data' in data and '__schema' in data['data']:
            for t in data['data']['__schema']['types']:
                if t['name'] == 'AudioUploadInput':
                    print('Fields for AudioUploadInput (from __schema):')
                    for fld in t.get('inputFields', []):
                        print(f"- {fld['name']}")
                    found = True
        
        if not found and 'data' in data and '__type' in data['data']:
            t = data['data']['__type']
            if t and t.get('name') == 'AudioUploadInput':
                print('Fields for AudioUploadInput (from __type):')
                for fld in t.get('inputFields', []):
                    print(f"- {fld['name']}")
                found = True

        if not found:
            print("No AudioUploadInput found in schema.")
            print("Keys:", list(data.get('data', {}).keys()))
    except Exception as e:
        print('Error parsing JSON:', e)
