# 🎵 X版Jockie Music

[日本語](README.md) | [English](README.en.md) | [中文](README.zh.md)

X (Twitter) の **スペースで動く音楽リクエストbot**。
Jockie Music（Discord）の非公式Xポートです。

**スペースツイートのリプにメンションするだけ**で、曲のリクエスト・キュー管理・再生ができます。

## ✨ 特徴

- 🎙️ **メンション方式** — スペースチャット（参加者しか見えない）ではなく、**スペースURLのツイートのリプにメンション**でコマンドを受け付け
- 🤝 **スピリク方式** — botはスペースを作らない。人間のスペースに参加 → スピーカーリクエスト → ホスト承認 → 音声出力
- 🎵 **Jockie Music互換コマンド** — play / skip / pause / shuffle / queue など30+コマンド
- 🔍 **3ソースのメンション監視** — 検索 + 通知欄 + スペースツイートのリプ欄（シャドウバン対策）
- 📊 **再生履歴** — 最近再生した曲の履歴を保持
- 🐳 **検証済み技術** — サンサンサンデー放送（29時間・514曲）で実証したWebRTC音声出力を応用

## 🚀 使い方

1. Xで**スペースを立てる**（Xが自動でスペースURLのツイートを投稿）
2. **そのスペースツイートのリプにメンション**してコマンドを送る：

```
@YourBot play 星野源 SUN
@YourBot play https://youtu.be/xxx
```

3. botが自動でスペースに参加 → **スピーカーリクエスト送信** → ホストが承認
4. キューに追加された曲を**順番にスペースで再生**

## 📋 主なコマンド

| カテゴリ | コマンド |
|---|---|
| Playback | `play` / `search` / `insert` / `join` / `leave` |
| Track State | `skip` / `pause` / `resume` / `forward` / `backward` / `windto` / `volume` |
| Queue State | `shuffle` / `reverse` / `sort` / `move` / `swap` |
| Information | `queue` / `np` / `nextup` / `recent` / `stats` |
| 管理 | `remove` / `clear` / `help` |

詳細は [docs](docs/) のコマンド一覧ページ（`pnpm --dir docs dev` で起動）または [X版Jockie Music Docs](https://maebahesioru.github.io/xjockiemusic/) を参照。

## 🔧 セットアップ

### 依存関係

```bash
pip install -r requirements.txt   # aiortc / av / yt-dlp / httpx / websockets
```

[PawiX25/twifork](https://github.com/PawiX25/twifork) をクローンしてパスを設定します：

```bash
git clone https://github.com/PawiX25/twifork
# config.json の twifork_path にクローン先を指定
```

### 設定

```bash
cp config.example.json config.json
```

`config.json` を編集：

| キー | 説明 |
|---|---|
| `cookie_path` | XのCookie（EditThisCookie形式のJSON） |
| `screen_name` | botアカウントの@名（@なし） |
| `twifork_path` | twiforkのクローン先パス |

### 起動

```bash
python bot.py
```

## 📁 構成

```
├── bot.py            # メイン（メンション監視・コマンド処理・再生ループ）
├── player.py         # SongTrack（WebRTC音声トラック・pause/seek/volume対応）
├── song_queue.py     # キュー管理（JSON永続化・shuffle/move/swap等）
├── config.example.json
├── requirements.txt
└── docs/             # ドキュメントサイト（Next.js・多言語対応）
```

## ⚠️ 注意

- これは**非公式**の個人プロジェクトです。本家Jockie Musicとは無関係です
- Cookieの取り扱いには十分注意してください（`config.json` はgit管理外）
- Xのレート制限・自動化検知には十分な間隔を空けて運用してください
