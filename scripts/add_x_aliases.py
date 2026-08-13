# X版対応コマンドに短縮エイリアス（x_alias）を追加 + X版専用コマンド（X-only）カテゴリを追加
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'docs', 'src', 'data', 'commands.json')

# 既存X版対応コマンドの短縮エイリアス
X_ALIASES = {
    'play': '!p', 'insert': '!i', 'join': '!j', 'leave': '!l',
    'pause': '!pa', 'resume': '!r', 'forward': '!f', 'backward': '!b',
    'volume': '!v', 'shuffle': '!sf', 'queue': '!q',
    'now playing': '!n / !np', 'next up': '!nu',
    'recently played': '!rc', 'session statistics': '!st',
}

# X版専用コマンド（公式Jockieにない・X版オリジナル）
X_ONLY = [
    {
        'command': 'skip', 'aliases': ['next', 's'], 'usage': 'skip',
        'description': 'Skip the current track', 'options': [], 'examples': [],
        'ja': '現在の曲をスキップします。例: !skip / !s',
        'x': True, 'x_alias': '!s / !next',
    },
    {
        'command': 'remove', 'aliases': ['rm'], 'usage': 'remove <number>',
        'description': 'Remove a track from the queue by number', 'options': [], 'examples': [],
        'ja': '指定番号の曲をキューから削除します。例: !remove 3 / !rm 3',
        'x': True, 'x_alias': '!rm',
    },
    {
        'command': 'clear', 'aliases': ['cl'], 'usage': 'clear',
        'description': 'Clear the entire queue', 'options': [], 'examples': [],
        'ja': 'キューを全消去します。例: !clear / !cl',
        'x': True, 'x_alias': '!cl',
    },
    {
        'command': 'help', 'aliases': ['h'], 'usage': 'help',
        'description': 'Show the command list', 'options': [], 'examples': [],
        'ja': 'コマンド一覧を表示します。例: !help / !h',
        'x': True, 'x_alias': '!h',
    },
]

with open(DATA, encoding='utf-8') as f:
    data = json.load(f)

# 既存コマンドのx_aliasを更新
for cat in data['categories']:
    for c in cat.get('commands', []):
        name = c.get('command', '')
        if name in X_ALIASES:
            c['x_alias'] = X_ALIASES[name]

# X-onlyカテゴリを追加（既にあれば置き換え）
data['categories'] = [c for c in data['categories'] if c.get('name') != 'X-only']
data['categories'].append({'name': 'X-only', 'commands': X_ONLY})

with open(DATA, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

print('✅ x_alias更新 + X-onlyカテゴリ追加（skip/remove/clear/help）')
