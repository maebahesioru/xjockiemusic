# コマンドデータに日本語説明とX版対応フラグを追加
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # プロジェクトルート
DATA = os.path.join(BASE, 'docs', 'src', 'data', 'commands.json')

# X版で実装済みのコマンド名（bot.pyのhandle_commandに対応）
X_SUPPORTED = {
    'play', 'search', 'insert', 'join', 'leave',
    'pause', 'resume', 'forward', 'backward', 'wind to', 'volume',
    'shuffle', 'reverse', 'sort', 'move', 'swap',
    'queue', 'now playing', 'next up', 'recently played', 'session statistics',
    'help', 'clean',
}
# botのエイリアスで動くもの
X_ALIASES = {
    'now playing': '!np / !nowplaying',
    'next up': '!nextup',
    'recently played': '!recent',
    'session statistics': '!stats',
    'wind to': '!windto 秒',
}

# 日本語説明（主要コマンド）
JA_DESC = {
    'play': '曲名やURLを検索してキューに追加します。スペースツイートのリプで「play 曲名」と送るだけ！',
    'search': '曲名を検索してキューに追加します（playと同じ動作）。',
    'insert': '再生中の曲の次に挿入します。すぐ聴きたい曲を割り込ませたい時に便利。',
    'join': 'スペースに参加します。スピーカーリクエスト（スピリク）を自動送信してホストの承認を待ちます。',
    'leave': 'スペースから離脱します。再生も停止します。',
    'pause': '再生を一時停止します（!resumeで再開）。',
    'resume': '一時停止した再生を再開します。',
    'forward': '再生位置を30秒進めます。',
    'backward': '再生位置を30秒戻します。',
    'wind to': '再生位置を指定した秒数に移動します。例: !windto 90',
    'volume': '音量を設定します（0〜200・100が標準）。例: !volume 150',
    'shuffle': 'キューをシャッフルします。',
    'reverse': 'キューを逆順にします。',
    'sort': 'キューを並べ替えます（title / user）。例: !sort title',
    'move': 'キューの曲を移動します。例: !move 3 5（3曲目を5番目へ）',
    'swap': 'キューの2曲を入れ替えます。例: !swap 1 2',
    'queue': '現在のキュー（再生待ちの曲）を表示します。',
    'now playing': '現在再生中の曲を表示します（!np / !nowplaying）。',
    'next up': '次に再生される曲を表示します（!nextup）。',
    'recently played': '最近再生した曲の履歴を表示します（!recent）。',
    'session statistics': '再生統計を表示します（!stats）。',
    'help': 'コマンド一覧を表示します。',
    'clean': 'botの関連ツイートを整理します。',
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
        if name in JA_DESC:
            cmd['ja'] = JA_DESC[name]
            count_ja += 1
        if name in X_ALIASES:
            cmd['x_alias'] = X_ALIASES[name]
for cmd in data.get('unknown', []):
    name = cmd.get('command', '')
    cmd['x'] = name in X_SUPPORTED
    if name in JA_DESC:
        cmd['ja'] = JA_DESC[name]

with open(DATA, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

print(f'✅ X版対応: {count_x}コマンド | 日本語説明: {count_ja}コマンド')
