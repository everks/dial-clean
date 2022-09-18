import json

def load_txt(path):
    with open(path, encoding='UTF-8', errors='ignore') as f:
        data = [i.strip() for i in f.readlines() if len(i.strip()) > 0]
    return data


def save_txt(data, path):
    with open(path, 'w', encoding='UTF-8') as f:
        f.write(data)

def save_json(data, path, indent=0):
    with open(path, 'w', encoding='UTF-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)

def save_jsonl(data, path):
    with open(path, 'w', encoding='UTF-8') as f:
        f.write("\n".join(json.dumps(line, ensure_ascii=False) for line in data))