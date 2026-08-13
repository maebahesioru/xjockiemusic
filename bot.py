# bot.py - X版Jockie Music メイン
# 方式: スペースURLのツイートのリプにメンションでコマンド → キュー操作・スペース再生
# コマンド（Jockie Music公式よりX版適応）:
#   play/search <曲名/URL> / insert <曲名/URL> / join / leave / pause / resume
#   skip / forward / backward / volume <0-200> / shuffle
#   sort [title|user] / move <from> <to> / swap <a> <b> / queue / np / nextup
#   recent / stats / remove <N> / clear / help
import asyncio
import json
import os
import re
import secrets
import sys
import time
import unicodedata

sys.path.insert(0, r'C:\Users\maeba\AppData\Local\Temp\twifork')
from twikit import Client
import yt_dlp

from song_queue import Queue
from player import SongTrack

def load_cfg():
    """config.json + 環境変数（Docker/Coolify用・環境変数優先）"""
    base = os.path.dirname(os.path.abspath(__file__))
    cfg = json.load(open(os.path.join(base, 'config.json'), encoding='utf-8'))
    env_map = {
        'COOKIE_JSON': 'cookie_json',   # CookieのJSON文字列（そのまま）
        'API_TOKEN': 'api_token',
        'SCREEN_NAME': 'screen_name',
        'API_PORT': 'api_port',
        'MAX_QUEUE': 'max_queue',
        'QUEUE_FILE': 'queue_file',
        'AUDIO_CACHE': 'audio_cache',
        'SPACE_TITLE': 'space_title',
    }
    for env_key, cfg_key in env_map.items():
        v = os.environ.get(env_key)
        if v:
            cfg[cfg_key] = v
    return cfg


CFG = load_cfg()

SPACE_URL_RE = re.compile(r'x\.com/i/spaces/([0-9A-Za-z]+)')
SPACE_TOKENS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'space_tokens.json')


def load_space_tokens():
    """スペーストークン（space_id→token）を読み込み"""
    if os.path.exists(SPACE_TOKENS_FILE):
        try:
            return json.load(open(SPACE_TOKENS_FILE, encoding='utf-8'))
        except Exception:
            pass
    return {}


def save_space_tokens(tokens):
    try:
        os.makedirs(os.path.dirname(SPACE_TOKENS_FILE), exist_ok=True)
        json.dump(tokens, open(SPACE_TOKENS_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    except Exception:
        pass


def get_space_token(space_id):
    """スペース専用のパネルトークンを取得（なければ生成）"""
    tokens = load_space_tokens()
    if space_id in tokens:
        return tokens[space_id]
    token = secrets.token_urlsafe(16)
    tokens[space_id] = token
    save_space_tokens(tokens)
    return token


def resolve_space_token(token):
    """トークンからスペースIDを解決（なければNone）"""
    tokens = load_space_tokens()
    for sid, tok in tokens.items():
        if tok == token:
            return sid
    return None
HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'data', 'history.json')


# ---------------------------------------------------------------- 曲の解決・DL
async def resolve(query):
    """曲名 or URL → (タイトル, URL, 長さ秒)"""
    url = query
    if not re.match(r'https?://', query):
        url = 'ytsearch1:' + query
    opts = {'quiet': True, 'noplaylist': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if 'entries' in info:
            info = info['entries'][0]
        dur = info.get('duration') or 0
        return info.get('title', query), info.get('webpage_url') or query, dur


def download_audio(url, dest_dir):
    """yt-dlpで音声をDLしてファイルパスを返す"""
    os.makedirs(dest_dir, exist_ok=True)
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(dest_dir, '%(id)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'restrictfilenames': True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        vid = info.get('id')
        for f in os.listdir(dest_dir):
            if f.startswith(vid):
                return os.path.join(dest_dir, f)
        return None


# ---------------------------------------------------------------- 履歴
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            return json.load(open(HISTORY_FILE, encoding='utf-8'))
        except Exception:
            return []
    return []


def save_history(history):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    json.dump(history[-50:], open(HISTORY_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)


# ---------------------------------------------------------------- スペース参加
async def join_space(client, track, space_id, sessions=None):
    """スペースに参加 → スピーカーリクエスト → 承認待ち → 音声出力"""
    try:
        print(f'[join] スペース参加: {space_id}')
        try:
            joined = await client.spaces.join(space_id, as_speaker=False, should_auto_join=True)
            print(f'[join] {joined}')
        except Exception as e:
            print(f'[join] ERR {str(e)[:120]}')
        suuid = await client.spaces.request_to_speak(space_id)
        print(f'[request] スピーカーリクエスト送信: {suuid}')
        await client.spaces.wait_for_speaker(space_id, suuid, timeout=7200)
        print('[approved] ホストに承認されました！')
        session = await client.spaces.speak(
            space_id,
            session_uuid=suuid,
            audio_track=track,
        )
        print(f'[speak] publisher_id={session.publisher_id} ice={session.pc.iceConnectionState}')
        print('🎵 スペースで再生可能になりました！')
        if sessions is not None:
            sessions['session'] = session
        return session
    except Exception as e:
        print(f'[join] スペース参加エラー: {e}')
        return None


# ---------------------------------------------------------------- メンション監視
async def process_tweet(client, tweet, queue, track, sessions, processed):
    """メンション検知→スペース特定→コントロールパネルURLをリプで返す"""
    tid = str(tweet.id)
    if tid in processed:
        return
    text = (tweet.text or '')
    if 'JockieMusicPort' not in text and 'jockiemusicport' not in text.lower():
        return
    user = getattr(tweet.user, 'screen_name', None) or '匿名'
    print(f'[tweet] @{user}: {text[:60]}')

    # スペースIDの特定: リプライ先ツイート → メンション内URL
    space_id = None
    reply_to = getattr(tweet, 'in_reply_to_status_id', None)
    if reply_to:
        try:
            parent = await client.get_tweet_by_id(reply_to)
            m = SPACE_URL_RE.search(parent.text or '')
            if m:
                space_id = m.group(1)
                print(f'[space] リプライ先からスペース特定: {space_id}')
        except Exception as e:
            print('リプライ先確認エラー:', str(e)[:100])
    if not space_id:
        m = SPACE_URL_RE.search(text)
        if m:
            space_id = m.group(1)
            print(f'[space] メンション内URLからスペース特定: {space_id}')
    if not space_id:
        return  # スペースが特定できなければ何もしない

    processed.add(tid)

    # スペース参加（初回のみ）
    if not sessions.get('space_id') or sessions['space_id'] != space_id:
        sessions['space_id'] = space_id
        asyncio.create_task(join_space(client, track, space_id, sessions))

    # スペース専用コントロールパネルURLを発行してリプで返す
    token = get_space_token(space_id)
    url = f'https://jockiemusic.hikamer.f5.si/control/{token}'
    await post_reply(client, tweet.id, f'🎛️ このスペースのコントロールパネル: {url}')


async def monitor_mentions(client, queue, track, sessions):
    """3ソースでメンションを監視（優先度順）:
    1. 通知欄（get_notifications('Mentions')・最速・シャドウバンも拾える）
    2. 参加中スペースのツイートのリプ欄（conversation_ids・最新順・確実）
    3. 検索（get_user_mentions・フォールバック・シャドウバンは拾えない）"""
    processed = set()
    pf = CFG['processed_file']
    if os.path.exists(pf):
        try:
            processed = set(json.load(open(pf, encoding='utf-8')))
        except Exception:
            pass

    while True:
        rate_limited = False

        # 1. 通知欄（最優先）
        try:
            notifs = await client.get_notifications('Mentions', count=40)
            for n in notifs:
                t = getattr(n, 'tweet', None)
                if t is not None:
                    await process_tweet(client, t, queue, track, sessions, processed)
        except Exception as e:
            print('通知エラー:', e)
            if '429' in str(e) or 'Rate limit' in str(e):
                rate_limited = True

        # 2. 参加中スペースのツイートのリプ欄（最新順・確実）
        try:
            stid = sessions.get('space_tweet_id')
            if stid:
                parent = await client.get_tweet_by_id(stid)
                # conversation_idsは関連度順の可能性があるため、ID降順（最新順）にソート
                ids = list(parent.conversation_ids or [])
                ids.sort(key=lambda x: int(x), reverse=True)
                for rid in ids:
                    if str(rid) in processed:
                        continue
                    try:
                        rt = await client.get_tweet_by_id(rid)
                        if rt is not None:
                            await process_tweet(client, rt, queue, track, sessions, processed)
                    except Exception:
                        pass
        except Exception as e:
            print('リプ欄エラー:', e)
            if '429' in str(e) or 'Rate limit' in str(e):
                rate_limited = True

        # 3. 検索（フォールバック）
        try:
            mentions = await client.get_user_mentions(CFG['screen_name'], count=20)
            for tweet in mentions:
                await process_tweet(client, tweet, queue, track, sessions, processed)
        except Exception as e:
            print('検索エラー:', e)
            if '429' in str(e) or 'Rate limit' in str(e):
                rate_limited = True

        try:
            os.makedirs(os.path.dirname(pf), exist_ok=True)
            json.dump(list(processed), open(pf, 'w', encoding='utf-8'), ensure_ascii=False)
        except Exception as e:
            print('保存エラー:', e)

        if rate_limited:
            print('⏳ レート制限中・5分バックオフ')
            await asyncio.sleep(300)
        await asyncio.sleep(CFG['poll_interval'])


# オプション解析: 「!play insert:true 曲名」「!play now:true 曲名」「!play sort:title 曲名」形式
# 全角「！」「：」も半角に正規化して判定（NFKC）
OPTION_NAMES = {'insert', 'now', 'remove', 'shuffle', 'reverse', 'search'}
OPTION_VALUES = {'sort', 'start', 'end', 'search-type'}

# コマンド短縮エイリアス（1〜2文字で操作できる）
CMD_ALIASES = {
    'play': ('play', 'p'),
    'insert': ('insert', 'i'),
    'join': ('join', 'j'),
    'leave': ('leave', 'l'),
    'pause': ('pause', 'pa'),
    'resume': ('resume', 'r'),
    'skip': ('skip', 'next', 's'),
    'forward': ('forward', 'f'),
    'backward': ('backward', 'b'),
    'volume': ('volume', 'v'),
    'shuffle': ('shuffle', 'sf'),
    'queue': ('queue', 'q'),
    'np': ('np', 'nowplaying', 'n'),
    'nextup': ('nextup', 'nu'),
    'recent': ('recent', 'rc'),
    'stats': ('stats', 'st'),
    'remove': ('remove', 'rm'),
    'clear': ('clear', 'cl'),
    'help': ('help', 'h'),
}


def get_command(cmd):
    """短縮エイリアスを正規コマンド名に解決"""
    for canonical, names in CMD_ALIASES.items():
        if cmd in names:
            return canonical
    return cmd


def parse_options(rest_norm, body_orig):
    """正規化済みrestからオプションを判定し、元の本文からクエリを切り出す"""
    opts = {}
    tokens_norm = rest_norm.split()
    tokens_orig = body_orig.split()
    qi = 0
    for i, (tn, _to) in enumerate(zip(tokens_norm, tokens_orig)):
        if ':' in tn:
            name, _, val = tn.partition(':')
            if name.lower() in OPTION_VALUES:
                opts[name.lower()] = val
                qi = i + 1
            elif name.lower() in OPTION_NAMES:
                # 値付きフラグ（insert:true 等）
                opts[name.lower()] = True
                qi = i + 1
            else:
                break
        elif tn in OPTION_NAMES:
            opts[tn] = True
            qi = i + 1
        else:
            break
    query = ' '.join(tokens_orig[qi:])
    return opts, query


async def handle_command(client, tweet, text, user, queue, track, sessions):
    """メンションのコマンドを処理（!あり/!なし両対応）"""
    # メンション部分を除去して、先頭のコマンドワードを抽出（全角！：もNFKCで半角化）
    body = re.sub(r'@\w+', '', text).strip()
    low = unicodedata.normalize('NFKC', body).lower()
    m = re.match(r'!?\s*([a-z0-9]+)', low)
    cmd = get_command(m.group(1) if m else '')
    rest = low[m.end():].strip() if m else ''

    # --- Playback系 ---
    if cmd == 'play':
        opts, query = parse_options(rest, re.sub(r'^!?\S+\s*', '', body))
        if not query:
            await post_reply(client, tweet.id, '🎵 曲名かURLを「play 曲名」で送ってね！（オプション: insert / now）')
            return
        # 未対応オプションはエラーを返す
        unsupported = set(opts) - {'insert', 'now'}
        if unsupported:
            await post_reply(client, tweet.id, f'❌ 未対応オプション: {" ".join(sorted(unsupported))}（対応: insert / now）')
            return
        if len(queue.list()) >= CFG['max_queue']:
            await post_reply(client, tweet.id, f'❌ キューがいっぱい（最大{CFG["max_queue"]}曲）')
            return
        title, url, dur = await resolve(query)
        if opts.get('insert') or opts.get('now'):
            queue.insert(title, url, user, 0)
            if opts.get('now'):
                track.skip()
                await post_reply(client, tweet.id, f'⚡ すぐ再生: {title}')
            else:
                await post_reply(client, tweet.id, f'⏩ 次の曲として挿入: {title}')
        else:
            n = queue.add(title, url, user)
            await post_reply(client, tweet.id, f'✅ {n}曲目に追加: {title}')

    elif cmd == 'insert':
        query = rest
        if not query:
            await post_reply(client, tweet.id, '🎵 「insert 曲名」で次の曲として挿入してね！')
            return
        title, url, dur = await resolve(query)
        pos = queue.insert(title, url, user, 0)
        await post_reply(client, tweet.id, f'⏩ 次の曲として挿入: {title}')

    elif cmd == 'join':
        sid = sessions.get('space_id')
        if sid and not sessions.get('session'):
            asyncio.create_task(join_space(client, track, sid, sessions))
            await post_reply(client, tweet.id, '🎙️ スペースに参加します！スピーカーリクエスト送信（ホストの承認待ち）')
        else:
            await post_reply(client, tweet.id, '🎙️ スペースツイートのリプにメンションしてね（スペースURLの自動検出）')

    elif cmd == 'leave':
        if sessions.get('session'):
            try:
                await sessions['session'].close()
            except Exception:
                pass
            sessions['session'] = None
            sessions['space_id'] = None
            await post_reply(client, tweet.id, '👋 スペースから離脱しました')

    # --- Track State系 ---
    elif cmd == 'pause':
        track.pause()
        await post_reply(client, tweet.id, '⏸️ 一時停止しました（resume で再開）')
    elif cmd == 'resume':
        track.resume()
        await post_reply(client, tweet.id, '▶️ 再開しました')
    elif cmd == 'skip':
        track.skip()
        await post_reply(client, tweet.id, '⏭️ スキップします')
    elif cmd == 'forward':
        track.seek(30)
        await post_reply(client, tweet.id, '⏩ +30秒 早送り')
    elif cmd == 'backward':
        track.seek(-30)
        await post_reply(client, tweet.id, '⏪ -30秒 巻き戻し')
    elif cmd == 'volume':
        m2 = re.search(r'(\d+)', rest)
        if m2:
            v = int(m2.group(1))
            track.set_volume(v)
            await post_reply(client, tweet.id, f'🔊 音量を {v} に設定')

    # --- Queue State系 ---
    elif cmd == 'shuffle':
        queue.shuffle()
        await post_reply(client, tweet.id, '🔀 シャッフルしました')
    # --- Information系 ---
    elif cmd == 'queue':
        items = queue.list()
        if not items:
            await post_reply(client, tweet.id, '📭 キューは空です')
        else:
            lines = [f'{i + 1}. {it["title"]}（{it["user"]}）' for i, it in enumerate(items[:10])]
            extra = f'\n... 他{len(items) - 10}曲' if len(items) > 10 else ''
            await post_reply(client, tweet.id, '📋 キュー:\n' + '\n'.join(lines) + extra)
    elif cmd == 'np':
        cur = sessions.get('current')
        if cur:
            await post_reply(client, tweet.id, f'🎵 再生中: {cur["title"]}（リクエスト: {cur["user"]}）')
        else:
            await post_reply(client, tweet.id, '🔇 再生中の曲はありません')
    elif cmd == 'nextup':
        items = queue.list()
        if items:
            await post_reply(client, tweet.id, f'⏭️ 次: {items[0]["title"]}')
        else:
            await post_reply(client, tweet.id, '📭 次の曲はありません')
    elif cmd == 'recent':
        hist = load_history()
        if hist:
            lines = [f'{i + 1}. {h["title"]}' for i, h in enumerate(hist[-5:][::-1])]
            await post_reply(client, tweet.id, '🕘 最近の曲:\n' + '\n'.join(lines))
        else:
            await post_reply(client, tweet.id, '🕘 履歴はまだありません')
    elif cmd == 'stats':
        hist = load_history()
        await post_reply(client, tweet.id, f'📊 再生済み: {len(hist)}曲 / キュー: {len(queue.list())}曲')

    # --- その他 ---
    elif cmd == 'remove':
        parts = rest.split()
        if len(parts) < 1:
            await post_reply(client, tweet.id, '❌ 使い方: remove 番号')
            return
        try:
            idx = int(parts[0]) - 1
            it = queue.remove(idx)
            await post_reply(client, tweet.id, f'🗑️ 削除: {it["title"]}' if it else '❌ その番号はないよ')
        except ValueError:
            await post_reply(client, tweet.id, '❌ 番号は数字で送ってね')
    elif cmd == 'clear':
        queue.clear()
        await post_reply(client, tweet.id, '🧹 キューを全消去しました')
    elif cmd == 'help':
        await post_reply(client, tweet.id,
                         '🎵 X版Jockie Music コマンド:\n'
                         'play 曲名/URL / insert 曲名（次の曲に）\n'
                         'skip / pause / resume / forward / backward / volume 数値\n'
                         'shuffle / queue / np / nextup / recent / stats / remove 番号 / clear / help')


_last_reply_time = 0.0
_reply_backoff_until = 0.0


async def post_reply(client, reply_to_id, text):
    """リプライ投稿（レート制限対策: 15秒間隔+429時5分バックオフ）"""
    global _last_reply_time, _reply_backoff_until
    now = time.time()
    # 429バックオフ中は送信しない（スキップ）
    if now < _reply_backoff_until:
        print(f'⏳ 送信バックオフ中（あと{int(_reply_backoff_until - now)}秒）・リプをスキップ')
        return
    # 送信間隔制限（15秒に1本まで・Xのレート制限対策）
    wait = _last_reply_time + 15 - now
    if wait > 0:
        await asyncio.sleep(wait)
    try:
        await client.create_tweet(text, reply_to=reply_to_id)
        _last_reply_time = time.time()
    except Exception as e:
        err = str(e)
        print('リプライ投稿エラー:', err[:120])
        if '429' in err or 'Rate limit' in err:
            _reply_backoff_until = time.time() + 300
            print('⏳ 送信レート制限検出・5分バックオフ開始')


# ---------------------------------------------------------------- 再生ループ
async def play_loop(client, queue, track, sessions):
    """再生ループ: キューから曲を取り出して順番に再生（スペース未参加なら待機）"""
    history = load_history()
    while True:
        if not sessions.get('session'):
            await asyncio.sleep(3)
            continue
        item = queue.next()
        if item is None:
            await asyncio.sleep(1)
            continue
        try:
            print(f'[download] {item["title"]}')
            path = await asyncio.to_thread(download_audio, item['url'], CFG['audio_cache'])
            if not path:
                print('ダウンロード失敗:', item['title'])
                continue
            track.load(path)
            sessions['current'] = item
            announce = f'🎵 再生中: {item["title"]}（リクエスト: {item["user"]}）'
            print(announce)
            try:
                await client.create_tweet(announce)
            except Exception as e:
                print('発表ツイートエラー:', str(e)[:120])
            await track.wait_ended()
            history.append(item)
            save_history(history)
            sessions['current'] = None
        except Exception as e:
            print('再生エラー:', e)


# ---------------------------------------------------------------- メイン
# グローバル状態（APIからアクセスするため）
G_client = None
G_track = None
G_sessions = None
G_queue = None
G_loop = None

# ---------------------------------------------------------------- Web API（サイト制御用）
from flask import Flask, request, jsonify
import threading

api_app = Flask(__name__)
API_TOKEN = CFG.get('api_token', '')


def api_auth_ok():
    """APIキー or スペーストークンで認証"""
    auth = request.headers.get('Authorization', '')
    token = auth.replace('Bearer ', '').strip()
    if API_TOKEN and token == API_TOKEN:
        return True
    # スペーストークン（/control/{token}用・発行済みトークンならOK）
    if resolve_space_token(token):
        return True
    return False


async def _noop():
    """何もしない（API用プレースホルダ）"""
    pass


def run_coro(coro, timeout=60):
    """botのイベントループ上でコルーチンを実行（APIスレッドから）"""
    future = asyncio.run_coroutine_threadsafe(coro, G_loop)
    return future.result(timeout=timeout)


@api_app.route('/api/status')
def api_status():
    if not api_auth_ok():
        return jsonify({'ok': False, 'error': 'unauthorized'}), 401
    cur = G_sessions.get('current') if G_sessions else None
    items = G_queue.list() if G_queue else []
    return jsonify({
        'ok': True,
        'current': cur,
        'queue': [{'title': it['title'], 'user': it['user']} for it in items],
        'queue_len': len(items),
        'space_id': G_sessions.get('space_id') if G_sessions else None,
        'joined': bool(G_sessions.get('session')) if G_sessions else False,
        'history_len': len(load_history()),
    })


@api_app.route('/api/play', methods=['POST'])
def api_play():
    if not api_auth_ok():
        return jsonify({'ok': False, 'error': 'unauthorized'}), 401
    d = request.get_json(force=True, silent=True) or {}
    query = (d.get('query') or '').strip()
    opts = d.get('opts') or {}
    if not query:
        return jsonify({'ok': False, 'error': 'queryが必要'}), 400
    try:
        title, url, dur = run_coro(resolve(query), timeout=60)
        if opts.get('insert') or opts.get('now'):
            G_queue.insert(title, url, d.get('user', 'site'), 0)
            if opts.get('now'):
                run_coro(G_track.skip() if hasattr(G_track, 'skip') else _noop())
                return jsonify({'ok': True, 'action': 'now', 'title': title})
            return jsonify({'ok': True, 'action': 'insert', 'title': title})
        n = G_queue.add(title, url, d.get('user', 'site'))
        return jsonify({'ok': True, 'action': 'add', 'title': title, 'pos': n})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)[:200]}), 500


@api_app.route('/api/skip', methods=['POST'])
def api_skip():
    if not api_auth_ok():
        return jsonify({'ok': False, 'error': 'unauthorized'}), 401
    G_track.skip()
    return jsonify({'ok': True})


@api_app.route('/api/pause', methods=['POST'])
def api_pause():
    if not api_auth_ok():
        return jsonify({'ok': False, 'error': 'unauthorized'}), 401
    G_track.pause()
    return jsonify({'ok': True})


@api_app.route('/api/resume', methods=['POST'])
def api_resume():
    if not api_auth_ok():
        return jsonify({'ok': False, 'error': 'unauthorized'}), 401
    G_track.resume()
    return jsonify({'ok': True})


@api_app.route('/api/volume', methods=['POST'])
def api_volume():
    if not api_auth_ok():
        return jsonify({'ok': False, 'error': 'unauthorized'}), 401
    d = request.get_json(force=True, silent=True) or {}
    v = int(d.get('value', 100))
    G_track.set_volume(max(0, min(200, v)))
    return jsonify({'ok': True, 'volume': v})


@api_app.route('/api/shuffle', methods=['POST'])
def api_shuffle():
    if not api_auth_ok():
        return jsonify({'ok': False, 'error': 'unauthorized'}), 401
    G_queue.shuffle()
    return jsonify({'ok': True})


@api_app.route('/api/clear', methods=['POST'])
def api_clear():
    if not api_auth_ok():
        return jsonify({'ok': False, 'error': 'unauthorized'}), 401
    G_queue.clear()
    return jsonify({'ok': True})


@api_app.route('/api/remove', methods=['POST'])
def api_remove():
    if not api_auth_ok():
        return jsonify({'ok': False, 'error': 'unauthorized'}), 401
    d = request.get_json(force=True, silent=True) or {}
    idx = int(d.get('index', 0)) - 1
    it = G_queue.remove(idx)
    return jsonify({'ok': True, 'removed': it['title'] if it else None})


@api_app.route('/api/join', methods=['POST'])
def api_join():
    if not api_auth_ok():
        return jsonify({'ok': False, 'error': 'unauthorized'}), 401
    d = request.get_json(force=True, silent=True) or {}
    url = (d.get('space_url') or '').strip()
    token = (d.get('token') or '').strip()
    sid = None
    if token:
        sid = resolve_space_token(token)
        if not sid:
            return jsonify({'ok': False, 'error': 'トークンが無効'}), 400
    else:
        m = SPACE_URL_RE.search(url)
        if not m:
            return jsonify({'ok': False, 'error': 'スペースURLが必要（https://x.com/i/spaces/...）'}), 400
        sid = m.group(1)
    G_sessions['space_id'] = sid
    asyncio.run_coroutine_threadsafe(join_space(G_client, G_track, sid, G_sessions), G_loop)
    return jsonify({'ok': True, 'space_id': sid})


@api_app.route('/api/leave', methods=['POST'])
def api_leave():
    if not api_auth_ok():
        return jsonify({'ok': False, 'error': 'unauthorized'}), 401
    async def _leave():
        if G_sessions.get('session'):
            try:
                await G_sessions['session'].close()
            except Exception:
                pass
            G_sessions['session'] = None
            G_sessions['space_id'] = None
    run_coro(_leave())
    return jsonify({'ok': True})


@api_app.route('/api/history')
def api_history():
    if not api_auth_ok():
        return jsonify({'ok': False, 'error': 'unauthorized'}), 401
    hist = load_history()
    return jsonify({'ok': True, 'history': hist[-20:][::-1]})


def start_api():
    # Docker（Coolify）内では0.0.0.0でバインド（API_HOST環境変数で切替）
    host = os.environ.get('API_HOST', '127.0.0.1')
    api_app.run(host=host, port=CFG.get('api_port', 8768), threaded=True)


async def main():
    global G_client, G_track, G_sessions, G_queue, G_loop
    G_loop = asyncio.get_event_loop()
    client = Client(language='ja')
    if CFG.get('cookie_json'):
        cookies = json.loads(CFG['cookie_json'])
    else:
        cookies = json.load(open(CFG['cookie_path'], encoding='utf-8'))
    client.set_cookies(cookies)
    uid = await client.user_id()
    print('✅ ログインOK user_id:', uid)
    G_client = client

    if '【' in CFG['screen_name']:
        print('❌ config.json の screen_name に bot の @名（@なし）を設定してね！')
        return

    G_track = SongTrack()
    G_sessions = {'session': None, 'space_id': None, 'current': None, 'pos': 0}
    G_queue = Queue(CFG['queue_file'])

    # Web APIサーバーを別スレッドで起動（サイト制御用）
    threading.Thread(target=start_api, daemon=True).start()
    print(f'🌐 APIサーバー起動: http://127.0.0.1:{CFG.get("api_port", 8768)}（トークン: {"設定済み" if API_TOKEN else "なし"}）')

    try:
        # メンション監視（パネルURL返却用）+ 再生ループ
        await asyncio.gather(
            monitor_mentions(client, G_queue, G_track, G_sessions),
            play_loop(client, G_queue, G_track, G_sessions),
        )
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        print('🛑 終了')


if __name__ == '__main__':
    asyncio.run(main())
