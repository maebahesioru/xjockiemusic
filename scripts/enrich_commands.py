# コマンドデータに日本語説明とX版対応フラグを追加（全96コマンド対応）
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

# 全96コマンドの日本語説明
JA_DESC = {
    # Meta
    'clean': 'botの関連ツイート（コマンド応答のリプライ）を全部削除して整理します。',
    'premium': 'プレミアムプランの情報を表示します。',
    'leaderboard': 'リーダーボードを表示します。',
    'leaderboard votes': 'botの投票（upvote）リーダーボードを表示します。',
    'vote': 'botリストで投票してbotを応援できます！',
    # Playback
    'autoplay toggle': 'オートプレイの切り替え。有効にするとキューが空になったとき関連曲を自動で追加します。',
    'play': '曲名やURLからトラックを検索してキューに追加します。スペースツイートのリプで「play 曲名」と送るだけ！',
    'playrecent': '最近再生した曲をキューに追加します。',
    'radio': 'ラジオ局を検索して再生します。',
    'resume session': '自分がオーナーだった直近のセッションを再開します。',
    'join': 'スペースに参加します。スピーカーリクエスト（スピリク）を自動送信してホストの承認を待ちます。',
    'leave': 'ボイスチャンネル（X版: スペース）から退出します。時間指定で遅延退出も可能。',
    'album search': 'アルバムを検索してキューに追加します。',
    'playlist search': 'プレイリストを検索してキューに追加します。',
    'search': '再生する曲を検索します（playと同じ動作）。',
    'insert': '現在再生中の曲の直後にトラックを挿入します。すぐ聴きたい曲を割り込ませたい時に便利。',
    'playleave': 'トラックをキューに追加し、再生が終わったらbotが退出します。',
    'playselect': 'URLからプレイリスト内の1曲を選んでキューに追加します。',
    'playsingle': 'URLからプレイリスト内の1曲をキューに追加します。',
    # Track State
    'backward': 'トラックを巻き戻します。時間指定可（0h 0m 0s形式）。X版では!backwardで30秒戻し。',
    'end time': '現在のトラックの終了位置を設定します。',
    'forward': 'トラックを早送りします。時間指定可。X版では!forwardで30秒進み。',
    'pause': '再生を一時停止します（!resumeで再開）。',
    'resume': '一時停止した再生を再開します。',
    'start time': '現在のトラックの開始位置を設定します。',
    'volume': '音量を変更します（デフォルト100・X版は0〜200）。例: !volume 150',
    'wind to': 'トラックの希望位置に移動します。X版: !windto 秒数',
    # Queue State
    'reverse': '現在のキューを逆順にします。',
    'shuffle': 'キューをシャッフルします。',
    'sort': 'キューを並べ替えます。X版: !sort title / !sort user',
    'mass move': 'キュー内の複数トラックをまとめて移動します（first/last指定可）。',
    'move': 'キュー内のトラックを移動します。X版: !move 3 5（3曲目を5番目へ）',
    'swap': 'キュー内の2つのトラックの位置を入れ替えます。X版: !swap 1 2',
    'reorder': '指定オプションでキューを並べ替えます。',
    # Information
    'next up': '次に再生されるトラックの情報を表示します（X版: !nextup）。',
    'now playing': '現在再生中のトラックを表示します（X版: !np / !nowplaying）。',
    'queue': 'キューの全リストを表示します（X版実装済み）。',
    'queue information': 'キューに関する情報を表示します。',
    'recently played': '最近聴いたトラックの履歴を表示します（X版: !recent）。',
    'requested': '各曲を誰がリクエストしたかを表示します。',
    'save': '現在の曲の情報をDMで送信します。',
    'session information': '現在のセッションの情報を表示します。',
    'session statistics': '現在のセッションの統計を表示します（X版: !stats）。',
    'upcoming': '今後のトラックのリストを表示します。',
    # Profile（Discord固有）
    'profile set server visibility': 'このサーバーでプロフィールデータを見られる人を設定します。',
    'profile': 'プロフィールを表示します。',
    'profile set avatar background': 'プロフィールのアバター背景を設定します。',
    'profile set avatar border': 'プロフィールのアバター枠を設定します。',
    'profile set avatar shape': 'プロフィールのアバター形状を設定します。',
    'profile set background': 'プロフィールの背景を設定します。',
    'profile set color': 'プロフィールの色を設定します。',
    'profile set privacy': 'プロフィールの公開範囲を設定します。',
    'profile set visibility': 'プロフィールを見られる人を設定します（public/private等）。',
    # Collection（Discord固有）
    'collection clone': 'コレクションを複製します。',
    'collection delete': 'コレクションを削除します。',
    'collection import': 'コレクションをインポートします。',
    'collection merge': '2つのコレクションを統合します。',
    'collections': 'コレクションの一覧を表示します。',
    'collection create': '新しいコレクションを作成します。',
    'collection save': '現在のキューをコレクションとして保存します。',
    'collection load': '既存のコレクションをキューに読み込んで再生します。',
    # Settings
    'settings': '現在の設定を表示します。',
    'settings reset': '設定をリセットします。',
    # Permissions（Discord固有）
    'permission allow': 'セッションの特定の権限を許可します。',
    'permission deny': 'セッションの特定の権限を拒否します。',
    'permissions': 'セッションまたはユーザーの権限を表示します。',
    'permissions allow all': 'すべての権限を許可します。',
    'permissions deny all': 'すべての権限を拒否します。',
    'permissions reset': '権限設定をリセットします。',
    # Owner（Discord固有）
    'claim ownership': 'セッションのオーナー権を主張します。',
    'rebind': 'アナウンスするチャンネルを更新します。',
    'transfer ownership': 'セッションのオーナー権を別のユーザーに譲渡します。',
    # Prefix
    'prefix list': '使用可能なプレフィックスの一覧を表示します。',
    # Server（Discord固有）
    'announce channel reset': '設定されているアナウンスチャンネルを解除します。',
    'announce channel set': 'アナウンスチャンネルを設定します。',
    'auto delete toggle': 'コマンドをトリガーしたメッセージを自動削除するか切り替えます。',
    '24/7': '24/7モードを切り替えます。有効にするとbotが自分から退出しなくなります。',
    'lock': 'セッションをロックして権限変更を無効化します。',
    'multi bot ownership': '複数botのオーナー設定を管理します。',
    'preferred bots server': 'サーバーでbotが参加する優先順を設定します。',
    'dashboard statistics access': 'サーバーのダッシュボード統計を見られる人を設定します。',
    'page replace delete toggle': 'ページ結果を置換するか削除するかを切り替えます。',
    'page delete toggle': 'ページ結果を削除するかどうかを切り替えます。',
    'timeout set': 'セッションのタイムアウト時間を設定します。',
    'timeouts': 'タイムアウトの一覧を表示します。',
    # User
    'auto correct toggle': 'コマンドの誤字を自動修正するか切り替えます。',
    'preferred bots': 'botが参加する優先順を設定します。',
    'volume automatic toggle': '自動デフォルト音量モードを切り替えます。',
    # Premium
    'collection import': 'コレクションをインポートします（プレミアム限定）。',
    # unknown（ページ操作）
    'previous page': 'ページ表示の前のページに移動します。',
    'go to page': 'ページ表示の任意のページに移動します。',
    'next page': 'ページ表示の次のページに移動します。',
    'cancel': 'ページ表示をキャンセルします。',
    'select': '選択肢から項目を選びます。',
    'renew': 'ページ表示を更新します。',
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
        count_ja += 1

with open(DATA, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

# 未翻訳チェック
missing = []
for cat in data['categories']:
    for cmd in cat.get('commands', []):
        if 'ja' not in cmd:
            missing.append(cmd.get('command', ''))
for cmd in data.get('unknown', []):
    if 'ja' not in cmd:
        missing.append(cmd.get('command', ''))

print(f'✅ X版対応: {count_x}コマンド | 日本語説明: {count_ja}コマンド')
if missing:
    print(f'⚠️ 未翻訳: {missing}')
else:
    print('✅ 全コマンドに日本語説明あり！')
