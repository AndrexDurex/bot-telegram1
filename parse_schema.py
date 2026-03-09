import json

with open('d:/YOP/BioAgent/fireflies_schema.json', 'r', encoding='utf-16le') as f:
    data = json.load(f)
    print("Schema Fields para AudioUploadInput:")
    if 'data' in data and data['data']['__type']:
        for field in data['data']['__type']['inputFields']:
            type_info = field['type']
            type_name = type_info.get('name') or (type_info.get('ofType') and type_info['ofType'].get('name'))
            print(f"- {field['name']}: {type_name} (kind: {type_info['kind']})")
