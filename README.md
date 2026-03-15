<div align="center">

# Transcript AI

**Transcribe & Summarize Any Audio or Video**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-Whisper-F55036?style=flat-square)](https://console.groq.com)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-LLM-7C3AED?style=flat-square)](https://openrouter.ai)
[![License](https://img.shields.io/badge/License-MIT-52b788?style=flat-square)](LICENSE)

</div>

---

<details open>
<summary><b>🇬🇧 English</b></summary>

## Overview

**Transcript AI** is a web application that automatically transcribes and summarizes any audio or video content. Upload an audio file, paste a YouTube URL, or paste existing text — the system handles everything in seconds.

Built with a warm dark theme, minimal UI, and animated waveform header.

## Features

| | Feature | Description |
|---|---|---|
| 🎙️ | **Audio Transcription** | `.mp3` / `.wav` via Groq Whisper API (cloud) or Faster-Whisper (local) |
| ▶️ | **YouTube** | Paste any URL → auto-download → transcribe → summarize |
| 📝 | **Paste Text** | Summarize any existing transcript instantly |
| 🤖 | **AI Summarization** | 6 output formats via OpenRouter |
| 📊 | **Keywords** | Auto-extracted keyword chips from every summary |
| ⏱️ | **Processing Time** | Shows transcription and total analysis duration |
| 🗂 | **History** | All results saved to SQLite with search, tags & re-export |
| 🏷️ | **Tags** | Label and organize history records |
| 💾 | **Export** | Download as `.txt` or `.docx` |
| ⚙️ | **Settings Popup** | Configure engine, model, API key in one place |

## Project Structure

```
transcript-ai/
├── app.py              ← Main Streamlit app
├── style.css           ← Dark warm theme
├── requirements.txt
├── .env                ← API Keys (never commit)
├── .gitignore
├── history.db          ← SQLite database (auto-created)
└── utils/
    ├── __init__.py
    ├── transcriber.py  ← Groq Whisper + Local Faster-Whisper
    ├── summarizer.py   ← Prompt templates + OpenRouter
    ├── exporter.py     ← .txt and .docx export
    └── database.py     ← SQLite CRUD + tags
```

## Installation

### 1. Install FFmpeg

```bash
# Windows
winget install Gyan.FFmpeg

# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt install ffmpeg
```

### 2. Clone & install dependencies

```bash
git clone https://github.com/your-username/transcript-ai.git
cd transcript-ai

python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
pip install groq yt-dlp python-dotenv
```

### 3. Configure API Keys

Create a `.env` file in the project root:

```env
# Groq — Speech-to-Text (free)
# Get key: https://console.groq.com
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx

# OpenRouter — LLM Summarization (free models available)
# Get key: https://openrouter.ai/keys
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx
```

### 4. Run

```bash
streamlit run app.py
```

Open `http://localhost:8501`

## How to Use

### First Run
1. Click any **Transcribe** or **Summarize** button
2. If no API key is set → **Settings popup** opens automatically
3. Enter your OpenRouter API Key and choose a model
4. Click **Save & Start** → processing begins immediately

### Audio Tab
- Upload `.mp3` or `.wav` file
- Click **Transcribe & Summarize**
- View transcript live as it processes
- Open Report → see summary + keywords + export options

### YouTube Tab
- Paste any YouTube URL
- Click **Download & Transcribe**
- Audio downloaded automatically via yt-dlp

### History Tab
- All results saved automatically
- Search by filename or content
- Click **View** to re-open any past report
- Add **Tags** to organize records
- Re-download `.txt` / `.docx` anytime
- Delete individual records

## Settings

### Speech-to-Text Engine

| Engine | Speed | Internet | Notes |
|---|---|---|---|
| **Groq API** ⭐ | ⚡⚡⚡⚡⚡ | Required | Free — 10–50× faster than CPU |
| **Local Whisper** | ⚡⚡ | Not needed | Higher privacy, slower |

Recommended: `whisper-large-v3-turbo`

### LLM Models (via OpenRouter)

| Model | Notes |
|---|---|
| `google/gemini-2.0-flash-001` | ⭐ Recommended — fast, free, Thai support |
| `google/gemini-2.5-pro-preview` | Higher quality, may cost |
| `meta-llama/llama-3.3-70b-instruct` | Free alternative |
| `deepseek/deepseek-chat-v3-0324` | Good for long content |
| `mistralai/mistral-small-3.1-24b-instruct` | Lightweight |
| `qwen/qwen-2.5-72b-instruct` | Strong multilingual |

### Summary Formats

| Format | Best For |
|---|---|
| ⚡ Quick Summary | Any content — fast read |
| 📋 Full Report | Meetings, lectures, interviews |
| 💡 Key Insights | Deep analysis, research |
| ✅ Action Items | Meetings, workshops |
| 🎤 Speaker Analysis | Debates, panels |
| 📰 Article | Publishing, communications |

## Processing Time Estimates

| Audio Length | Groq API | Local Whisper (small) |
|---|---|---|
| 10 min | ~15–30 sec | ~8 min |
| 30 min | ~45–90 sec | ~25 min |
| 60 min | ~2–3 min | ~50 min |

> Files over 25 MB are automatically split into chunks.

## Troubleshooting

| Error | Fix |
|---|---|
| `FFmpeg not found` | Install FFmpeg and add to PATH |
| `Groq 413 File Too Large` | `pip install pydub` — auto-chunking handles it |
| `OpenRouter 429` | Rate limit reached — wait or switch models |
| `NameError: get_stats` | Use latest `app.py` with database import |
| Dialog opens on delete | Use latest `app.py` — fixed |

## License

MIT — free for personal and commercial use.

</details>

---

<details>
<summary><b>🇹🇭 ภาษาไทย</b></summary>

## ภาพรวม

**Transcript AI** คือเว็บแอปที่ถอดความและสรุปเนื้อหาจากเสียงหรือวิดีโอได้ทุกประเภทอัตโนมัติ อัปโหลดไฟล์เสียง วาง URL YouTube หรือวางข้อความ — ระบบจัดการทุกอย่างให้ในไม่กี่วินาที

## ฟีเจอร์

| | ฟีเจอร์ | รายละเอียด |
|---|---|---|
| 🎙️ | **ถอดความเสียง** | `.mp3` / `.wav` ผ่าน Groq Whisper API หรือ Faster-Whisper |
| ▶️ | **YouTube** | วาง URL → ดาวน์โหลดอัตโนมัติ → ถอดความ → สรุป |
| 📝 | **วางข้อความ** | สรุป transcript ที่มีอยู่แล้วทันที |
| 🤖 | **สรุปด้วย AI** | 6 รูปแบบ ผ่าน OpenRouter |
| 📊 | **Keywords** | สกัด keyword อัตโนมัติจากทุก summary |
| ⏱️ | **เวลาประมวลผล** | แสดงเวลาที่ใช้ถอดความและสรุป |
| 🗂 | **ประวัติ** | บันทึกลง SQLite ค้นหา แท็ก และ export ย้อนหลังได้ |
| 🏷️ | **Tags** | ติดป้ายกำกับจัดหมวดหมู่รายการ |
| 💾 | **Export** | ดาวน์โหลดเป็น `.txt` หรือ `.docx` |
| ⚙️ | **Settings Popup** | ตั้งค่า engine, model, API key ในที่เดียว |

## โครงสร้างไฟล์

```
transcript-ai/
├── app.py              ← Streamlit app หลัก
├── style.css           ← Dark warm theme
├── requirements.txt
├── .env                ← API Keys (ห้าม commit)
├── .gitignore
├── history.db          ← SQLite database (สร้างอัตโนมัติ)
└── utils/
    ├── __init__.py
    ├── transcriber.py  ← Groq Whisper + Local Faster-Whisper
    ├── summarizer.py   ← Prompt templates + OpenRouter
    ├── exporter.py     ← Export .txt และ .docx
    └── database.py     ← SQLite CRUD + tags
```

## การติดตั้ง

### 1. ติดตั้ง FFmpeg

```bash
# Windows
winget install Gyan.FFmpeg

# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt install ffmpeg
```

### 2. Clone และติดตั้ง

```bash
git clone https://github.com/your-username/transcript-ai.git
cd transcript-ai

python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
pip install groq yt-dlp python-dotenv
```

### 3. ตั้งค่า API Keys

สร้างไฟล์ `.env`:

```env
# Groq — ถอดความเสียง (ฟรี)
# สมัครที่: https://console.groq.com
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx

# OpenRouter — สรุปด้วย LLM (ฟรีบางโมเดล)
# สมัครที่: https://openrouter.ai/keys
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx
```

### 4. รันแอป

```bash
streamlit run app.py
```

เปิด `http://localhost:8501`

## วิธีใช้งาน

### ครั้งแรก
1. กดปุ่ม Transcribe หรือ Summarize ใดก็ได้
2. ถ้ายังไม่มี API Key → **Settings popup เด้งขึ้นอัตโนมัติ**
3. ใส่ OpenRouter API Key และเลือกโมเดล
4. กด **Save & Start** → เริ่มประมวลผลทันที

### Tab Audio
- อัปโหลดไฟล์ `.mp3` หรือ `.wav`
- กด **Transcribe & Summarize**
- ดู transcript แบบ real-time ขณะประมวลผล
- เปิด Report → ดู summary + keywords + download

### Tab YouTube
- วาง URL YouTube ใดก็ได้
- กด **Download & Transcribe**
- ดาวน์โหลดเสียงอัตโนมัติผ่าน yt-dlp

### Tab History
- ผลลัพธ์ทุกครั้งบันทึกอัตโนมัติ
- ค้นหาจากชื่อไฟล์หรือเนื้อหา
- กด **View** เพื่อเปิดรายงานเดิม
- เพิ่ม **Tags** จัดหมวดหมู่
- Download ย้อนหลังได้ตลอด

## ประมาณเวลาประมวลผล

| ความยาว | Groq API | Local Whisper (small) |
|---|---|---|
| 10 นาที | ~15–30 วินาที | ~8 นาที |
| 30 นาที | ~45–90 วินาที | ~25 นาที |
| 60 นาที | ~2–3 นาที | ~50 นาที |

## ปัญหาที่พบบ่อย

| ปัญหา | วิธีแก้ |
|---|---|
| `FFmpeg not found` | ติดตั้ง FFmpeg และเพิ่มใน PATH |
| `Groq 413 Too Large` | `pip install pydub` |
| `OpenRouter 429` | ถึง rate limit — รอหรือเปลี่ยนโมเดล |
| Dialog เปิดตอนลบ | ใช้ `app.py` เวอร์ชันล่าสุด |

## License

MIT — ใช้งานได้อิสระ ทั้งส่วนตัวและองค์กร

</details>

---

<div align="center">
  <sub>Built with ❤️ &nbsp;·&nbsp; Transcript AI</sub>
</div>