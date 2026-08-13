# bot.py - X版Jockie Music メイン
# 方式: スペースURLのツイートのリプにメンションでコマンド → キュー操作・スペース再生
# コマンド（Jockie Music公式よりX版適応）:
#   play/search <曲名/URL> / insert <曲名/URL> / join / leave / pause / resume
#   skip / forward / backward / windto <秒> / volume <0-200> / shuffle / reverse
#   sort [title|user] / move <from> <to> / swap <a> <b> / queue / np / nextup
#   recent / stats / remove <N> / clear / help
import asyncio
import json
import os
import re
import sys
import time

sys.path.insert(0, r'C:\Users\maeba\AppData\Local\Temp\twifork')
from twikit import Client
import yt_dlp

from song_queue import Queue
from player import SongTrack

CFG = json.load(open(os.path.join(os.path.dirname(__file__), 'config.json'), encoding='utf-8'))

SPACE_URL_RE = re.compile(r'x\.com/i/spaces/([0-9A-Za-z]+)')
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
async def monitor_mentions(client, queue, track, sessions):
    """メンション監視: スペース特定 → 参加 / 全コマンド処理"""
    processed = set()
    pf = CFG['processed_file']
    if os.path.exists(pf):
        try:
            processed = set(json.load(open(pf, encoding='utf-8')))
        except Exception:
            pass

    while True:
        try:
            mentions = await client.get_user_mentions(CFG['screen_name'], count=20)
            for tweet in mentions:
                tid = str(tweet.id)
                if tid in processed:
                    continue
                processed.add(tid)
                text = (tweet.text or '')
                user = getattr(tweet.user, 'screen_name', None) or '匿名'
                print(f'[mention] @{user}: {text[:60]}')

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

                # スペース参加（初回のみ）
                if space_id and (not sessions.get('space_id') or sessions['space_id'] != space_id):
                    sessions['space_id'] = space_id
                    asyncio.create_task(join_space(client, track, space_id, sessions))
                    await post_reply(client, tweet.id, '🎙️ スペースに参加します！スピーカーリクエスト送信（ホストの承認待ち）')

                # コマンド処理
                try:
                    await handle_command(client, tweet, text, user, queue, track, sessions)
                except Exception as e:
                    print('コマンド処理エラー:', e)

            os.makedirs(os.path.dirname(pf), exist_ok=True)
            json.dump(list(processed), open(pf, 'w', encoding='utf-8'), ensure_ascii=False)
        except Exception as e:
            print('メンション監視エラー:', e)
            if '429' in str(e) or 'Rate limit' in str(e):
                await asyncio.sleep(300)  # レート制限は5分バックオフ
                continue
        await asyncio.sleep(CFG['poll_interval'])


async def handle_command(client, tweet, text, user, queue, track, sessions):
    """メンションのコマンドを処理"""
    low = text.lower()

    # --- Playback系 ---
    if re.search(r'(?<!\w)(?:play|p)\s', low):
        m2 = re.search(r'(?<!\w)(?:play|p)\s+(.+)', text, re.I)
        query = m2.group(1).strip() if m2 else ''
        if not query:
            await post_reply(client, tweet.id, '🎵 曲名かURLを「!play 曲名」で送ってね！')
            return
        if len(queue.list()) >= CFG['max_queue']:
            await post_reply(client, tweet.id, f'❌ キューがいっぱい（最大{CFG["max_queue"]}曲）')
            return
        title, url, dur = await resolve(query)
        n = queue.add(title, url, user)
        await post_reply(client, tweet.id, f'✅ {n}曲目に追加: {title}')

    elif '!search' in low:
        m2 = re.search(r'!search\s+(.+)', text)
        query = m2.group(1).strip() if m2 else ''
        if not query:
            await post_reply(client, tweet.id, '🎵 「!search 曲名」で検索してね！')
            return
        title, url, dur = await resolve(query)
        n = queue.add(title, url, user)
        await post_reply(client, tweet.id, f'🔍 検索結果を追加: {title}（{n}曲目）')

    elif '!insert' in low:
        m2 = re.search(r'!insert\s+(.+)', text)
        query = m2.group(1).strip() if m2 else ''
        if not query:
            await post_reply(client, tweet.id, '🎵 「!insert 曲名」で次の曲として挿入してね！')
            return
        title, url, dur = await resolve(query)
        pos = queue.insert(title, url, user, 0)
        await post_reply(client, tweet.id, f'⏩ 次の曲として挿入: {title}')

    elif '!join' in low:
        sid = sessions.get('space_id')
        if sid and not sessions.get('session'):
            asyncio.create_task(join_space(client, track, sid, sessions))
            await post_reply(client, tweet.id, '🎙️ スペースに参加します！スピーカーリクエスト送信（ホストの承認待ち）')
        else:
            await post_reply(client, tweet.id, '🎙️ スペースツイートのリプにメンションしてね（スペースURLの自動検出）')

    elif '!leave' in low:
        if sessions.get('session'):
            try:
                await sessions['session'].close()
            except Exception:
                pass
            sessions['session'] = None
            sessions['space_id'] = None
            await post_reply(client, tweet.id, '👋 スペースから離脱しました')

    # --- Track State系 ---
    elif '!pause' in low:
        track.pause()
        await post_reply(client, tweet.id, '⏸️ 一時停止しました（!resume で再開）')
    elif '!resume' in low:
        track.resume()
        await post_reply(client, tweet.id, '▶️ 再開しました')
    elif '!skip' in low or '!next' in low:
        track.skip()
        await post_reply(client, tweet.id, '⏭️ スキップします')
    elif '!forward' in low:
        track.seek(30)
        await post_reply(client, tweet.id, '⏩ +30秒 早送り')
    elif '!backward' in low:
        track.seek(-30)
        await post_reply(client, tweet.id, '⏪ -30秒 巻き戻し')
    elif re.search(r'!windto\s+\d', low):
        m2 = re.search(r'!windto\s+(\d+)', low)
        if m2:
            secs = int(m2.group(1))
            track.seek(secs - (sessions.get('pos', 0)))
            sessions['pos'] = secs
            await post_reply(client, tweet.id, f'🎯 {secs}秒の位置へ移動')
    elif re.search(r'!volume\s+\d', low):
        m2 = re.search(r'!volume\s+(\d+)', low)
        if m2:
            v = int(m2.group(1))
            track.set_volume(v)
            await post_reply(client, tweet.id, f'🔊 音量を {v} に設定')

    # --- Queue State系 ---
    elif '!shuffle' in low:
        queue.shuffle()
        await post_reply(client, tweet.id, '🔀 シャッフルしました')
    elif '!reverse' in low:
        queue.reverse()
        await post_reply(client, tweet.id, '🔄 キューを逆順にしました')
    elif re.search(r'!sort', low):
        key = 'title'
        m2 = re.search(r'!sort\s+(\w+)', low)
        if m2:
            key = m2.group(1)
        queue.sort_by(key if key in ('title', 'user') else 'title')
        await post_reply(client, tweet.id, f'🗂️ キューを {key} で並べ替えました')
    elif re.search(r'!move\s+\d', low):
        parts = re.findall(r'\d+', text)
        if len(parts) >= 2:
            frm, to = int(parts[0]) - 1, int(parts[1]) - 1
            it = queue.move(frm, to)
            await post_reply(client, tweet.id, f'📦 移動: {it["title"]}' if it else '❌ 範囲外の番号')
    elif re.search(r'!swap\s+\d', low):
        parts = re.findall(r'\d+', text)
        if len(parts) >= 2:
            a, b = int(parts[0]) - 1, int(parts[1]) - 1
            ok = queue.swap(a, b)
            await post_reply(client, tweet.id, '🔄 入れ替えました' if ok else '❌ 範囲外の番号')

    # --- Information系 ---
    elif '!queue' in low or re.search(r'!q\b', low):
        items = queue.list()
        if not items:
            await post_reply(client, tweet.id, '📭 キューは空です')
        else:
            lines = [f'{i + 1}. {it["title"]}（{it["user"]}）' for i, it in enumerate(items[:10])]
            extra = f'\n... 他{len(items) - 10}曲' if len(items) > 10 else ''
            await post_reply(client, tweet.id, '📋 キュー:\n' + '\n'.join(lines) + extra)
    elif '!np' in low or '!nowplaying' in low:
        cur = sessions.get('current')
        if cur:
            await post_reply(client, tweet.id, f'🎵 再生中: {cur["title"]}（リクエスト: {cur["user"]}）')
        else:
            await post_reply(client, tweet.id, '🔇 再生中の曲はありません')
    elif '!nextup' in low:
        items = queue.list()
        if items:
            await post_reply(client, tweet.id, f'⏭️ 次: {items[0]["title"]}')
        else:
            await post_reply(client, tweet.id, '📭 次の曲はありません')
    elif '!recent' in low:
        hist = load_history()
        if hist:
            lines = [f'{i + 1}. {h["title"]}' for i, h in enumerate(hist[-5:][::-1])]
            await post_reply(client, tweet.id, '🕘 最近の曲:\n' + '\n'.join(lines))
        else:
            await post_reply(client, tweet.id, '🕘 履歴はまだありません')
    elif '!stats' in low:
        hist = load_history()
        await post_reply(client, tweet.id, f'📊 再生済み: {len(hist)}曲 / キュー: {len(queue.list())}曲')

    # --- その他 ---
    elif '!remove' in low:
        parts = text.split()
        if len(parts) < 2:
            await post_reply(client, tweet.id, '❌ 使い方: !remove 番号')
            return
        try:
            idx = int(parts[1]) - 1
            it = queue.remove(idx)
            await post_reply(client, tweet.id, f'🗑️ 削除: {it["title"]}' if it else '❌ その番号はないよ')
        except ValueError:
            await post_reply(client, tweet.id, '❌ 番号は数字で送ってね')
    elif '!clear' in low:
        queue.clear()
        await post_reply(client, tweet.id, '🧹 キューを全消去しました')
    elif '!help' in low:
        await post_reply(client, tweet.id,
                         '🎵 X版Jockie Music コマンド:\n'
                         '!play 曲名/URL / !insert 曲名（次の曲に）\n'
                         '!skip / !pause / !resume / !forward / !backward / !volume 数値\n'
                         '!shuffle / !reverse / !move A B / !swap A B / !sort\n'
                         '!queue / !np / !nextup / !recent / !stats / !remove 番号 / !clear / !help')


async def post_reply(client, reply_to_id, text):
    """リプライ投稿（エラーは握りつぶす）"""
    try:
        await client.create_tweet(text, reply_to=reply_to_id)
    except Exception as e:
        print('リプライ投稿エラー:', str(e)[:120])


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
async def main():
    client = Client(language='ja')
    cookies = json.load(open(CFG['cookie_path'], encoding='utf-8'))
    client.set_cookies(cookies)
    uid = await client.user_id()
    print('✅ ログインOK user_id:', uid)

    if '【' in CFG['screen_name']:
        print('❌ config.json の screen_name に bot の @名（@なし）を設定してね！')
        return

    track = SongTrack()
    sessions = {'session': None, 'space_id': None, 'current': None, 'pos': 0}
    queue = Queue(CFG['queue_file'])

    try:
        await asyncio.gather(
            monitor_mentions(client, queue, track, sessions),
            play_loop(client, queue, track, sessions),
        )
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        print('🛑 終了')


if __name__ == '__main__':
    asyncio.run(main())
