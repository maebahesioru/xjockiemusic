# 文字化け修正 + 全オプション日本語訳
# 正しい日本語はgitの25018b7版（文字化け前）から取得
import json
import os
import subprocess

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'docs', 'src', 'data', 'commands.json')

# 1. gitの25018b7版（文字化け前の正しいデータ）からja説明を取得
out = subprocess.check_output(
    ['git', 'show', '25018b7:docs/src/data/commands.json'],
    cwd=BASE,
)
old_data = json.loads(out.decode('utf-8'))
OLD_JA = {}
for cat in old_data['categories']:
    for c in cat.get('commands', []):
        if c.get('ja'):
            OLD_JA[c['command']] = c['ja']
for c in old_data.get('unknown', []):
    if c.get('ja'):
        OLD_JA[c['command']] = c['ja']

# 2. 対応コマンドは実装ベースの説明で上書き
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
JA_DESC = dict(OLD_JA)
JA_DESC.update(JA_IMPLEMENTED)

# 3. オプション日本語訳（部分一致パターン・先勝ち）
OPT_PATTERNS = [
    ('The message id to stop at, this is the last message it will delete', '削除を停止するメッセージID（最新から数えて最後に削除するメッセージ）'),
    ('The message id to start from, this is the first message it will delete', '削除を開始するメッセージID（最新から数えて最初に削除するメッセージ）'),
    ('Sort the playlist before adding it', '追加前にプレイリストを並べ替える（title/author/lengthで指定）'),
    ('Sort the album before adding it', '追加前にアルバムを並べ替える（title/author/lengthで指定）'),
    ('Sort the tracks, possible values', '曲を並べ替える（title/author/lengthで指定）'),
    ('Sort the view list', '一覧を並べ替える（title/author/lengthで指定）'),
    ('Make the track start at the specified time', '指定した時間から再生を開始'),
    ('Make the track end at the specified time', '指定した時間で再生を終了'),
    ('Select which page you want to load for a Spotify playlist', 'Spotifyプレイリストの読み込むページを選択'),
    ('Shuffle the playlist before adding it', '追加前にプレイリストをシャッフル'),
    ('Shuffle the album before adding it', '追加前にアルバムをシャッフル'),
    ('Shuffle the collection before adding it', '追加前にコレクションをシャッフル'),
    ('Reverse the playlist before adding it', '追加前にプレイリストを逆順にする'),
    ('Reverse the album before adding it', '追加前にアルバムを逆順にする'),
    ('Reverse the collection before adding it', '追加前にコレクションを逆順にする'),
    ('Insert the tracks right after the current song', '現在の曲の直後に挿入'),
    ('Insert the track right after the current song', '現在の曲の直後に挿入'),
    ('Insert the collection right after the current song', '現在の曲の直後にコレクションを挿入'),
    ('Play the tracks right away', 'すぐに再生'),
    ('Play the track right away', 'すぐに再生'),
    ('Play the collection right away', 'すぐに再生'),
    ('Display all the search results instead of getting the first', '最初の1件だけでなく全検索結果を表示'),
    ('Remove the track after it has been played', '再生後に曲をキューから削除'),
    ('Remove the tracks in the collection after they have been played', '再生後にコレクションの曲を削除'),
    ('Play the selected track in a playlist and only that track', 'プレイリスト内の選択した曲だけを再生'),
    ('Play the selected track in an album and only that track', 'アルバム内の選択した曲だけを再生'),
    ('Similar to `single` but lets you select which track', 'singleに似ているが再生する曲を選べる'),
    ('Similar to --single but lets you select which track', 'singleに似ているが再生する曲を選べる'),
    ('Search tracks with one of', 'soundcloud/spotify/deezer/apple-music等から検索元を指定'),
    ('Queue all of the tracks from the search result', '検索結果の全曲をキューに追加'),
    ('Queue all recently played tracks', '最近再生した全曲をキューに追加'),
    ('Force it to pause instead of toggling', '一時停止/再開の切替でなく強制的に一時停止'),
    ('Restart the queue and skip the currently playing', 'キューを最初から再生して現在の曲をスキップ'),
    ('Keep the shuffled position of the currently playing', '現在の曲のシャッフル位置を維持'),
    ('Shuffle the upcoming tracks', '今後の曲をシャッフル'),
    ('Reverse the sort type', '並べ替えの向きを反転（lengthは短い順→長い順に変わる）'),
    ('Reorder the upcoming tracks', '今後の曲を並べ替える'),
    ('Filter the leaderboard by people in this server', 'このサーバーのメンバーでリーダーボードを絞り込む'),
    ('See the top upvotes all-time', '全期間のトップ投票数を表示'),
    ('Search for a location and then show all stations', '場所を検索してその地域の全ラジオ局を表示'),
    ('Search for a country and show all stations', '国を検索してその国の全ラジオ局を表示'),
    ('Select a random station of the results', '結果からランダムなラジオ局を選択'),
    ('Using this will display the entire queue of the session', 'セッションの全キューを表示（再生は開始しない）'),
    ('Filter the tracks by an author', '作者で曲を絞り込む'),
    ('Filter the tracks by a title', 'タイトルで曲を絞り込む'),
    ('Reverse the tracks', '曲を逆順にする'),
    ('Include who requested the track', 'リクエストした人を表示'),
    ('Only show the upcoming tracks', '今後の曲だけを表示'),
    ('Get additional information such as ids', 'ID等の追加情報を表示'),
    ('Display the track queue index instead of upcoming', 'キュー番号を表示（今後の番号でなく）'),
    ('Reverse the view list', '一覧を逆順にする'),
    ('force the command to use the server', 'サーバー設定を対象にする'),
    ('force the command to use your own', '自分の設定を対象にする'),
    ('force the command to use the session', 'セッション設定を対象にする'),
    ('View all personal prefixes', '自分のプレフィックス一覧を表示'),
    ('View all server prefixes', 'サーバーのプレフィックス一覧を表示'),
    ('Show the currently set value for each of the bots', '各botの現在の設定値を表示'),
    ('Resets the value, if used in combination with a bot argument', '設定値をリセット（bot指定と併用するとそのbotのみ）'),
]


def translate_option(desc: str) -> str | None:
    for pat, ja in OPT_PATTERNS:
        if desc.startswith(pat):
            return ja
    return None


# 4. commands.jsonを修正
with open(DATA, encoding='utf-8') as f:
    data = json.load(f)

untranslated = []
for cat in data['categories']:
    for c in cat.get('commands', []):
        name = c.get('command', '')
        if name in JA_DESC:
            c['ja'] = JA_DESC[name]
        for o in c.get('options', []):
            oja = translate_option(o.get('description', ''))
            if oja:
                o['ja'] = oja
            else:
                untranslated.append((name, o.get('name', ''), o.get('description', '')[:60]))
for c in data.get('unknown', []):
    name = c.get('command', '')
    if name in JA_DESC:
        c['ja'] = JA_DESC[name]
    for o in c.get('options', []):
        oja = translate_option(o.get('description', ''))
        if oja:
            o['ja'] = oja
        else:
            untranslated.append((name, o.get('name', ''), o.get('description', '')[:60]))

with open(DATA, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

# 5. 結果確認
print('=== 未訳オプション ===')
for cmd, oname, desc in untranslated:
    print(f'[{cmd}] {oname}: {desc}')
print(f'未訳数: {len(untranslated)}')
