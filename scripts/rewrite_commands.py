# bot.pyのhandle_commandを「!あり/!なし両対応」に書き換える
import re

path = r'C:\Users\maeba\Desktop\xjockiemusic\bot.py'
with open(path, encoding='utf-8') as f:
    src = f.read()

new_func = '''async def handle_command(client, tweet, text, user, queue, track, sessions):
    """メンションのコマンドを処理（!あり/!なし両対応）"""
    # メンション部分を除去して、先頭のコマンドワードを抽出
    body = re.sub(r'@\\w+', '', text).strip()
    low = body.lower()
    m = re.match(r'!?\\s*([a-z0-9]+)', low)
    cmd = m.group(1) if m else ''
    rest = low[m.end():].strip() if m else ''

    # --- Playback系 ---
    if cmd in ('play', 'p'):
        query = rest
        if not query:
            await post_reply(client, tweet.id, '🎵 曲名かURLを「play 曲名」で送ってね！')
            return
        if len(queue.list()) >= CFG['max_queue']:
            await post_reply(client, tweet.id, f'❌ キューがいっぱい（最大{CFG["max_queue"]}曲）')
            return
        title, url, dur = await resolve(query)
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
    elif cmd in ('skip', 'next'):
        track.skip()
        await post_reply(client, tweet.id, '⏭️ スキップします')
    elif cmd == 'forward':
        track.seek(30)
        await post_reply(client, tweet.id, '⏩ +30秒 早送り')
    elif cmd == 'backward':
        track.seek(-30)
        await post_reply(client, tweet.id, '⏪ -30秒 巻き戻し')
    elif cmd == 'volume':
        m2 = re.search(r'(\\d+)', rest)
        if m2:
            v = int(m2.group(1))
            track.set_volume(v)
            await post_reply(client, tweet.id, f'🔊 音量を {v} に設定')

    # --- Queue State系 ---
    elif cmd == 'shuffle':
        queue.shuffle()
        await post_reply(client, tweet.id, '🔀 シャッフルしました')
    # --- Information系 ---
    elif cmd in ('queue', 'q'):
        items = queue.list()
        if not items:
            await post_reply(client, tweet.id, '📭 キューは空です')
        else:
            lines = [f'{i + 1}. {it["title"]}（{it["user"]}）' for i, it in enumerate(items[:10])]
            extra = f'\\n... 他{len(items) - 10}曲' if len(items) > 10 else ''
            await post_reply(client, tweet.id, '📋 キュー:\\n' + '\\n'.join(lines) + extra)
    elif cmd in ('np', 'nowplaying'):
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
            await post_reply(client, tweet.id, '🕘 最近の曲:\\n' + '\\n'.join(lines))
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
                         '🎵 X版Jockie Music コマンド:\\n'
                         'play 曲名/URL / insert 曲名（次の曲に）\\n'
                         'skip / pause / resume / forward / backward / volume 数値\\n'
                         'shuffle / queue / np / nextup / recent / stats / remove 番号 / clear / help')


'''

# handle_command関数の開始から _last_reply_time の前までを置換
start = src.index('async def handle_command(client, tweet, text, user, queue, track, sessions):')
end = src.index('_last_reply_time = 0.0')
src = src[:start] + new_func + src[end:]

with open(path, 'w', encoding='utf-8') as f:
    f.write(src)
print('handle_command書き換え完了')
