# コマンドデータのX版対応フラグ更新のみ（ja説明は触らない）
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'docs', 'src', 'data', 'commands.json')

# X版で実装済みのコマンド名（bot.pyのhandle_commandに対応）
X_SUPPORTED = {
    'play', 'insert', 'join', 'leave',
    'pause', 'resume', 'forward', 'backward', 'volume',
    'shuffle',
    'queue', 'now playing', 'next up', 'recently played', 'session statistics',
    'help',
}
X_ALIASES = {
    'now playing': '!np / !nowplaying',
    'next up': '!nextup',
    'recently played': '!recent',
    'session statistics': '!stats',
}

with open(DATA, encoding='utf-8') as f:
    data = json.load(f)

count_x = 0
for cat in data['categories']:
    for cmd in cat.get('commands', []):
        name = cmd.get('command', '')
        cmd['x'] = name in X_SUPPORTED
        if name in X_SUPPORTED:
            count_x += 1
        if name in X_ALIASES:
            cmd['x_alias'] = X_ALIASES[name]
        else:
            cmd.pop('x_alias', None)
for cmd in data.get('unknown', []):
    name = cmd.get('command', '')
    cmd['x'] = name in X_SUPPORTED
    if name in X_SUPPORTED:
        count_x += 1

with open(DATA, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

print(f'✅ X版対応: {count_x}コマンド')
