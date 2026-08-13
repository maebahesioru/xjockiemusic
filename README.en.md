# 🎵 Jockie Music for X

[日本語](README.md) | [English](README.en.md) | [中文](README.zh.md)

A **music request bot that runs in X (Twitter) Spaces**.
An unofficial X port of Jockie Music (Discord).

**Just mention the bot in a reply to your Space tweet** to request, queue, and play music.

## ✨ Features

- 🎙️ **Mention-based** — Commands are accepted via **mentions in replies to the Space URL tweet** (not Space chat, which is only visible to participants)
- 🤝 **Speaker-request flow** — The bot doesn't create Spaces. It joins your Space → sends a speaker request → host approves → streams audio
- 🎵 **Jockie Music-compatible commands** — play / skip / pause / shuffle / queue and 30+ more
- 🔍 **3-source mention monitoring** — search + notifications + Space tweet reply thread (shadowban-resistant)
- 📊 **Play history** — Keeps a history of recently played tracks
- 🐳 **Proven tech** — WebRTC audio output battle-tested in the 29-hour, 514-track "Sunsun Sunday" broadcast

## 🚀 Usage

1. **Start a Space** on X (X automatically posts the Space URL tweet)
2. **Reply to the Space tweet** mentioning the bot with a command:

```
@YourBot play 星野源 SUN
@YourBot play https://youtu.be/xxx
```

3. The bot joins automatically → **sends a speaker request** → the host approves
4. Queued tracks are **played in the Space in order**

## 📋 Main commands

| Category | Commands |
|---|---|
| Playback | `play` / `search` / `insert` / `join` / `leave` |
| Track State | `skip` / `pause` / `resume` / `forward` / `backward` / `windto` / `volume` |
| Queue State | `shuffle` / `reverse` / `sort` / `move` / `swap` |
| Information | `queue` / `np` / `nextup` / `recent` / `stats` |
| Management | `remove` / `clear` / `help` |

See the [docs](docs/) command list page (run `pnpm --dir docs dev`) or [Jockie Music for X Docs](https://maebahesioru.github.io/xjockiemusic/en/).

## 🔧 Setup

### Dependencies

```bash
pip install -r requirements.txt   # aiortc / av / yt-dlp / httpx / websockets
```

Clone [PawiX25/twifork](https://github.com/PawiX25/twifork) and set the path:

```bash
git clone https://github.com/PawiX25/twifork
# set twifork_path in config.json
```

### Configuration

```bash
cp config.example.json config.json
```

Edit `config.json`:

| Key | Description |
|---|---|
| `cookie_path` | X cookies (EditThisCookie-format JSON) |
| `screen_name` | Bot account @name (without @) |
| `twifork_path` | Path to the twifork clone |

### Run

```bash
python bot.py
```

## 📁 Structure

```
├── bot.py            # Main (mention monitoring, command handling, play loop)
├── player.py         # SongTrack (WebRTC audio track, pause/seek/volume)
├── song_queue.py     # Queue management (JSON persistence, shuffle/move/swap)
├── config.example.json
├── requirements.txt
└── docs/             # Documentation site (Next.js, multilingual)
```

## 💝 Donate

If you'd like to support this project:

**https://ofuse.me/maebahesioru**

## ⚠️ Notes

- This is an **unofficial** personal project. Not affiliated with the original Jockie Music
- Handle cookies with care (`config.json` is git-ignored)
- Respect X rate limits and automation detection by keeping reasonable intervals
