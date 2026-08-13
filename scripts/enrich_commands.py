# コマンドデータに日本語説明とX版対応フラグを追加（X版対応コマンドのみ）
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # プロジェクトルート
DATA = os.path.join(BASE, 'docs', 'src', 'data', 'commands.json')

# X版で実装済みのコマンド名（bot.pyのhandle_commandに対応）
X_SUPPORTED = {
    'play', 'search', 'insert', 'join', 'leave',
    'pause', 'resume', 'forward', 'backward', 'wind to', 'volume',
    'shuffle', 'reverse', 'sort', 'move', 'swap',
    'queue', 'now playing', 'next up', 'recently played', 'session statistics',
    'help',
}
# botのエイリアスで動くもの
X_ALIASES = {
    'now playing': '!np / !nowplaying',
    'next up': '!nextup',
    'recently played': '!recent',
    'session statistics': '!stats',
    'wind to': '!windto 秒',
}

# X版対応コマンドの日本語説明（実装ベースのみ・簡潔に）
JA_DESC = {
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

with open(DATA, encoding='utf-8') as f:
    data = json.load(f)

count_x = 0
count_ja = 0
for cat in data['categories']:
    for cmd in cat.get('commands', []):
        name = cmd.get('command', '')
        cmd['x'] = name in X_SUPPORTED
        if name in X_SUPPORTED:
            count_x += 1
            cmd['ja'] = JA_DESC[name]
            count_ja += 1
        else:
            # 非対応コマンドの説明は消す（ハルシネーション防止）
            cmd.pop('ja', None)
            cmd.pop('x_alias', None)
        if name in X_ALIASES:
            cmd['x_alias'] = X_ALIASES[name]
for cmd in data.get('unknown', []):
    name = cmd.get('command', '')
    cmd['x'] = name in X_SUPPORTED
    if name in X_SUPPORTED:
        cmd['ja'] = JA_DESC[name]
        count_ja += 1
    else:
        cmd.pop('ja', None)

with open(DATA, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

print(f'✅ X版対応: {count_x}コマンド | 日本語説明: {count_ja}コマンド')
