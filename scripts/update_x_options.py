# X版対応コマンドのoptionsを「X版で実際に動くオプション」だけに書き換える
# 入力方式: コマンド内に直接（例: !play insert 曲名 / !play now 曲名）
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'docs', 'src', 'data', 'commands.json')

X_OPTIONS = {
    'play': [
        {'name': 'insert', 'description': 'Insert as the next track. Usage: !play insert <song>', 'ja': '次の曲として挿入します。例: !play insert 曲名'},
        {'name': 'now', 'description': 'Play right away. Usage: !play now <song>', 'ja': 'すぐに再生します。例: !play now 曲名'},
    ],
    'insert': [
        {'name': 'now', 'description': 'Play right away. Usage: !insert now <song>', 'ja': 'すぐに再生します。例: !insert now 曲名'},
    ],
    'pause': [],
    'resume': [],
    'forward': [],
    'backward': [],
    'volume': [],
    'shuffle': [],
    'queue': [],
    'now playing': [],
    'next up': [],
    'recently played': [],
    'session statistics': [],
    'join': [],
    'leave': [],
}

with open(DATA, encoding='utf-8') as f:
    data = json.load(f)

changed = 0
for cat in data['categories']:
    for c in cat.get('commands', []):
        name = c.get('command', '')
        if name in X_OPTIONS:
            c['options'] = X_OPTIONS[name]
            changed += 1
            print(f'✅ {name}: optionsをX版用に書き換え（{len(X_OPTIONS[name])}個）')

with open(DATA, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

print(f'変更: {changed}コマンド')
