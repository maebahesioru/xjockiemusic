# 全96コマンドに日本語説明を付与（対応コマンドは実装ベース・非対応は正確な訳）
# 前のJA_DESC（enrich_old.py）をベースに、対応コマンドの説明を実装ベースで上書き
import json, os, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'docs', 'src', 'data', 'commands.json')

# 前の96コマンド版JA_DESCを取得
old_src = open(os.path.join(BASE, 'scripts', 'enrich_old.py'), encoding='utf-8').read()
m = re.search(r'JA_DESC = \{(.*?)\n\}', old_src, re.S)
OLD_JA = {}
for k, v in re.findall(r"'([\w ]+)':\s*'((?:[^'\\]|\\.)*)'", m.group(1)):
    OLD_JA[k] = v.encode().decode('unicode_escape').replace("\\'", "'")

# X版で実装済みのコマンド名
X_SUPPORTED = {
    'play', 'search', 'insert', 'join', 'leave',
    'pause', 'resume', 'forward', 'backward', 'wind to', 'volume',
    'shuffle', 'reverse', 'sort', 'move', 'swap',
    'queue', 'now playing', 'next up', 'recently played', 'session statistics',
    'help',
}
X_ALIASES = {
    'now playing': '!np / !nowplaying',
    'next up': '!nextup',
    'recently played': '!recent',
    'session statistics': '!stats',
    'wind to': '!windto 秒',
}

# 対応コマンドの説明は実装ベースの簡潔版（ハルシネーションなし）
JA_IMPLEMENTED = {
    'play': '曲名やURLを検索してキューに追加します。例: !play 星野源 SUN',
    'search': '曲名を検索してキューに追加します（playと同じ動作）。例: !search 曲名',
    'insert': '次の曲としてキューに挿入します。例: !insert 曲名',
    'join': 'スペースに参加してスピーカーリクエストを送信します。例: !join',
    'leave': 'スペースから離脱して再生を停止します。例: !leave',
    'pause': '再生を一時停止します。例: !pause',
    'resume': '一時停止した再生を再開します。例: !resume',
    'forward': '再生位置を30秒進めます。例: !forward',
    'backward': '再生位置を30秒戻します。例: !backward',
    'wind to': '再生位置を指定秒数に移動します。例: !windto 90',
    'volume': '音量を変更します（0〜200・標準100）。例: !volume 150',
    'shuffle': 'キューをシャッフルします。例: !shuffle',
    'reverse': 'キューを逆順にします。例: !reverse',
    'sort': 'キューを並べ替えます。例: !sort title',
    'move': 'キューの曲を移動します。例: !move 3 5',
    'swap': 'キューの2曲を入れ替えます。例: !swap 1 2',
    'queue': '現在のキューを表示します。例: !queue',
    'now playing': '現在再生中の曲を表示します。例: !np',
    'next up': '次に再生される曲を表示します。例: !nextup',
    'recently played': '最近再生した曲を表示します。例: !recent',
    'session statistics': '再生統計を表示します。例: !stats',
    'help': 'コマンド一覧を表示します。例: !help',
}

# マージ: 対応コマンド=実装ベース・非対応=前の正確な訳
JA_DESC = dict(OLD_JA)
JA_DESC.update(JA_IMPLEMENTED)
# スラッシュ入りキー（正規表現で拾えなかったもの）
JA_DESC['24/7'] = '24/7モードを切り替えます。有効にするとbotが自分から退出しなくなります。'

with open(DATA, encoding='utf-8') as f:
    data = json.load(f)

count_ja = 0
missing = []
for cat in data['categories']:
    for cmd in cat.get('commands', []):
        name = cmd.get('command', '')
        cmd['x'] = name in X_SUPPORTED
        if name in JA_DESC:
            cmd['ja'] = JA_DESC[name]
            count_ja += 1
        else:
            missing.append(name)
        if name in X_ALIASES:
            cmd['x_alias'] = X_ALIASES[name]
for cmd in data.get('unknown', []):
    name = cmd.get('command', '')
    cmd['x'] = name in X_SUPPORTED
    if name in JA_DESC:
        cmd['ja'] = JA_DESC[name]
        count_ja += 1
    else:
        missing.append(name)

with open(DATA, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

print(f'✅ 日本語説明: {count_ja}コマンド')
if missing:
    print(f'⚠️ 説明なし: {missing}')
else:
    print('✅ 全96コマンドに日本語説明あり！')
