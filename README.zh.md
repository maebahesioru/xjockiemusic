# 🎵 X版Jockie Music（Jockie Music for X）

[日本語](README.md) | [English](README.en.md) | [中文](README.zh.md)

在 X（Twitter）**Space 中运行的音乐点歌机器人**。
Jockie Music（Discord）的非官方 X 移植版。

**只需在 Space 推文的回复中提及机器人**，即可点歌、管理队列和播放。

## ✨ 特点

- 🎙️ **提及方式** — 命令通过**在 Space 链接推文的回复中提及机器人**来接收（而非只有参与者可见的 Space 聊天）
- 🤝 **发言请求流程** — 机器人不创建 Space。加入你的 Space → 发送发言请求 → 主持人批准 → 输出音频
- 🎵 **Jockie Music 兼容命令** — play / skip / pause / shuffle / queue 等 30+ 个命令
- 🔍 **3 路提及监控** — 搜索 + 通知栏 + Space 推文回复串（防影子封禁）
- 📊 **播放历史** — 保存最近播放的歌曲记录
- 🐳 **实战验证技术** — 在 29 小时、514 首曲目的广播中验证过的 WebRTC 音频输出

## 🚀 使用方法

1. 在 X 上**开启 Space**（X 会自动发布 Space 链接推文）
2. **在 Space 推文的回复中**提及机器人并发送命令：

```
@YourBot play 星野源 SUN
@YourBot play https://youtu.be/xxx
```

3. 机器人自动加入 → **发送发言请求** → 主持人批准
4. 队列中的歌曲将**按顺序在 Space 中播放**

## 📋 主要命令

| 分类 | 命令 |
|---|---|
| 播放 | `play` / `search` / `insert` / `join` / `leave` |
| 曲目状态 | `skip` / `pause` / `resume` / `forward` / `backward` / `windto` / `volume` |
| 队列状态 | `shuffle` / `reverse` / `sort` / `move` / `swap` |
| 信息 | `queue` / `np` / `nextup` / `recent` / `stats` |
| 管理 | `remove` / `clear` / `help` |

详细命令列表请查看 [docs](docs/)（运行 `pnpm --dir docs dev`）或 [X版Jockie Music 文档](https://maebahesioru.github.io/xjockiemusic/zh/)。

## 🔧 安装

### 依赖

```bash
pip install -r requirements.txt   # aiortc / av / yt-dlp / httpx / websockets
```

克隆 [PawiX25/twifork](https://github.com/PawiX25/twifork) 并设置路径：

```bash
git clone https://github.com/PawiX25/twifork
# 在 config.json 中设置 twifork_path
```

### 配置

```bash
cp config.example.json config.json
```

编辑 `config.json`：

| 键 | 说明 |
|---|---|
| `cookie_path` | X 的 Cookie（EditThisCookie 格式 JSON） |
| `screen_name` | 机器人账号的 @名（不含 @） |
| `twifork_path` | twifork 克隆路径 |

### 运行

```bash
python bot.py
```

## 📁 结构

```
├── bot.py            # 主程序（提及监控、命令处理、播放循环）
├── player.py         # SongTrack（WebRTC 音频轨道，支持暂停/跳转/音量）
├── song_queue.py     # 队列管理（JSON 持久化，shuffle/move/swap 等）
├── config.example.json
├── requirements.txt
└── docs/             # 文档网站（Next.js，多语言）
```

## 💝 捐赠

如果您想支持这个项目：

**https://ofuse.me/maebahesioru**

## ⚠️ 注意

- 这是**非官方**的个人项目，与本家 Jockie Music 无关
- 请小心处理 Cookie（`config.json` 不在 git 管理范围内）
- 请注意 X 的速率限制和自动化检测，保持合理的间隔
