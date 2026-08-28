import json, pathlib
p = pathlib.Path('data/publications.json')
data = json.loads(p.read_text(encoding='utf-8'))
before = len(data)
data = [e for e in data if (e.get('doi') or '').lower() != '10.7554/elife.60265.sa2']
p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(f"removed eLife author-response entry: {before} -> {len(data)}")
