# 使わないコマンドの処理をbot.pyから削除（search/sort/reverse/move/swap/windto）
import re

path = r'C:\Users\maeba\Desktop\xjockiemusic\bot.py'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# 削除対象: ブロック開始行のパターン
targets = [
    "elif '!search' in low:",
    "elif re.search(r'!windto\\s+\\d', low):",
    "elif '!reverse' in low:",
    "elif re.search(r'!sort', low):",
    "elif re.search(r'!move\\s+\\d', low):",
    "elif re.search(r'!swap\\s+\\d', low):",
]


def find_block_start(lines, pat):
    for i, ln in enumerate(lines):
        if ln.strip().startswith(pat):
            return i
    return None


def remove_block(lines, start_idx):
    """start_idxのブロックを次にelif/#/空行が来るまで削除"""
    i = start_idx
    while i < len(lines):
        if i != start_idx and lines[i].strip().startswith('elif ') or (i != start_idx and lines[i].strip().startswith('#')):
            break
        i += 1
    # 行末まで削除（ブロック内）
    return lines[:start_idx] + lines[i:]


removed = []
for pat in targets:
    idx = find_block_start(lines, pat)
    if idx is None:
        print(f'⚠️ 見つからない: {pat}')
        continue
    lines = remove_block(lines, idx)
    removed.append(pat)
    print(f'✅ 削除: {pat}')

# helpテキストの行を修正
for i, ln in enumerate(lines):
    if "'!shuffle / !reverse / !move A B / !swap A B / !sort" in ln:
        lines[i] = ln.replace(
            "'!shuffle / !reverse / !move A B / !swap A B / !sort\\n'",
            "'!shuffle / !insert 曲名\\n'",
        )
        print('✅ helpテキスト修正:', i + 1)

# ヘッダーコメント修正
for i, ln in enumerate(lines):
    if 'windto <秒> / volume <0-200> / shuffle / reverse' in ln:
        lines[i] = ln.replace(
            '#   skip / forward / backward / windto <秒> / volume <0-200> / shuffle / reverse',
            '#   skip / forward / backward / volume <0-200> / shuffle',
        )
        print('✅ ヘッダーコメント修正:', i + 1)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('完了')
