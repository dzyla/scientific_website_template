import json, pathlib
p = pathlib.Path('data/publications.json')
data = json.loads(p.read_text(encoding='utf-8'))

JP_DUP = "胆汁応答性シャペロンとしての代謝産物結合蛋白質ムーンライト【JST・京大機械翻訳】"
before = len(data)
data = [e for e in data if e.get("title") != JP_DUP]
print(f"removed Japanese EMBO-J duplicate: {before} -> {len(data)}")

for e in data:
    if e.get("title", "").startswith("Drugie stanowisko Myrmeleon"):
        e["journal"] = "Acta Entomologica Silesiana"
        e["link"] = "https://www.researchgate.net/publication/273949540_Drugie_stanowisko_Myrmeleon_inconspicuus_Rambur_1842_w_Polsce_Neuroptera_Myrmeleontidae"
        print("fixed Myrmeleon entry: journal -> Acta Entomologica Silesiana (vol 12-13: 161-162), added link")
        print("  authors:", e["authors"], "| bold:", e["highlight"])

p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("saved", len(data), "entries")
