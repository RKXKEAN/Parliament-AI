<div align="center">
  <img src="https://img.shields.io/badge/Parliament%20AI-Thai%20Legislative%20System-c9a84c?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iI2M5YTg0YyIgZD0iTTEyIDJMMyA3djJoMTh2LTJMMTB6TTMgMTl2MmgxOHYtMmgtMnYtOGgtMnY4aC0ydi04SDl2OEg3di04SDV2OHoiLz48L3N2Zz4=" />
  <br/><br/>

# 🏛️ Parliament AI

  <p>
    <a href="#-english"><img src="https://img.shields.io/badge/🇬🇧-English-1a237e?style=flat-square" /></a>
    &nbsp;
    <a href="#-ภาษาไทย"><img src="https://img.shields.io/badge/🇹🇭-ภาษาไทย-c9a84c?style=flat-square" /></a>
  </p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" />
    <img src="https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" />
    <img src="https://img.shields.io/badge/Groq-Whisper_API-F55036?style=flat-square" />
    <img src="https://img.shields.io/badge/OpenRouter-LLM-7C3AED?style=flat-square" />
    <img src="https://img.shields.io/badge/License-MIT-52b788?style=flat-square" />
  </p>
</div>

---

<!-- ════════════════════════════════════════════════════════════
     🇬🇧  ENGLISH
     ════════════════════════════════════════════════════════════ -->

## 🇬🇧 English

<details open>
<summary><b>Click to expand / collapse</b></summary>

### Overview

**Parliament AI** is an AI-powered web application that automatically transcribes and summarizes Thai parliamentary sessions. Upload an audio file, paste a YouTube link, or paste existing text — the system handles the rest.

### ✨ Features

| Feature | Description |
|---|---|
| 🎙️ **Audio Transcription** | `.mp3` & `.wav` via Groq API (cloud) or Faster-Whisper (local CPU) |
| ▶️ **YouTube Support** | Paste URL → auto-download audio → transcribe → summarize |
| 📝 **Paste Text** | Instantly summarize any existing transcript |
| 🤖 **AI Summarization** | OpenRouter & Google Gemini supported |
| 📋 **6 Summary Formats** | Official report / Brief / Political analysis / Resolutions / Speaker analysis / Press release |
| 💾 **Export** | Download reports as `.txt` and `.docx` |
| 🎨 **Parliament Dark Gold UI** | Custom gold & navy theme |

### 📁 Project Structure

```
parliament-transcriber/
├── app.py                  ← Main Streamlit application
├── style.css               ← Parliament Dark Gold theme
├── requirements.txt        ← Python dependencies
├── .env                    ← API Keys (never commit to Git)
├── .gitignore
└── utils/
    ├── transcriber.py      ← Groq Whisper API + Local Faster-Whisper
    ├── summarizer.py       ← Prompt templates + OpenRouter/Gemini
    └── exporter.py         ← .txt and .docx export
```

### 🚀 Installation

**1. Install FFmpeg**

```bash
# Ubuntu / Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
winget install Gyan.FFmpeg
```

**2. Clone & install dependencies**

```bash
git clone https://github.com/your-username/parliament-transcriber.git
cd parliament-transcriber

python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

pip install -r requirements.txt
pip install groq yt-dlp python-dotenv
```

**3. Configure API Keys**

Create a `.env` file in the project root:

```env
# Groq API — Speech-to-Text (free)
# Register at: https://console.groq.com
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx

# OpenRouter — LLM summarization (free models available)
# Register at: https://openrouter.ai/keys
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx

# Google Gemini — alternative LLM (optional)
# Register at: https://aistudio.google.com/apikey
GEMINI_API_KEY=AIza-xxxxxxxxxxxx
```

**4. Run the app**

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

### ⚙️ Configuration

**Speech-to-Text Engine**

| Engine | Speed | Internet | Notes |
|---|---|---|---|
| **Groq API** ⭐ | ⚡⚡⚡⚡⚡ | Required | Free — 10–50× faster than CPU |
| **Local Whisper** | ⚡⚡ | Not needed | Higher privacy, slower |

**Recommended Groq model:** `whisper-large-v3-turbo`

**LLM Provider**

| Provider | Recommended Model | Free |
|---|---|---|
| **OpenRouter** | `google/gemini-2.0-flash-001` | ✅ |
| **Google Gemini** | `gemini-2.0-flash` | ✅ (without billing) |

**Summary Formats**

| Format | Best For |
|---|---|
| 📋 Full Official Report | Government records, formal documents |
| ⚡ Brief Summary | Executives, journalists |
| 🏛️ Political Analysis | Researchers, analysts |
| ✅ Resolutions & Action Items | Administration, task tracking |
| 🎤 Speaker Analysis | Reporters, researchers |
| 📰 Press Release | PR, communications teams |

### 📊 Estimated Processing Time

| Audio Length | Groq API | Local Whisper (small) |
|---|---|---|
| 10 min | ~15–30 sec | ~8 min |
| 30 min | ~45–90 sec | ~25 min |
| 60 min | ~2–3 min | ~50 min |
| 120 min | ~4–6 min | ~100 min |

> Files larger than 25 MB are automatically split into chunks.

### 🐛 Troubleshooting

| Problem | Solution |
|---|---|
| `FFmpeg not found` | Install FFmpeg and ensure it's in your system PATH |
| `Groq 413 File Too Large` | Install pydub: `pip install pydub` — auto-chunking will handle it |
| `OpenRouter 429` | Rate limit reached — wait a moment or switch models |
| `latin-1 codec error` | Update to latest `summarizer.py` |
| Sidebar widgets disappear | Update to latest `app.py` (all widgets have explicit `key=`) |

### 🔒 Security

- API Keys stored in `.env` — **never commit to Git**
- Uploaded audio files are deleted automatically after processing
- No data is permanently stored

### 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | [Streamlit](https://streamlit.io) |
| STT (Cloud) | [Groq Whisper API](https://console.groq.com) |
| STT (Local) | [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) |
| LLM | [OpenRouter](https://openrouter.ai) / [Google Gemini](https://aistudio.google.com) |
| YouTube | [yt-dlp](https://github.com/yt-dlp/yt-dlp) |
| Audio | [FFmpeg](https://ffmpeg.org) / [pydub](https://github.com/jiaaro/pydub) |
| Export | [python-docx](https://python-docx.readthedocs.io) |
| Styling | Custom CSS — Parliament Dark Gold |

### 📄 License

MIT License — free for personal and commercial use.

</details>

---

<!-- ════════════════════════════════════════════════════════════
     🇹🇭  THAI
     ════════════════════════════════════════════════════════════ -->

## 🇹🇭 ภาษาไทย

<details>
<summary><b>คลิกเพื่อเปิด / ปิด</b></summary>

### ภาพรวม

**Parliament AI** คือเว็บแอปพลิเคชันที่ใช้ AI ถอดความและสรุปการประชุมรัฐสภาไทยโดยอัตโนมัติ อัปโหลดไฟล์เสียง วาง YouTube URL หรือวางข้อความที่มีอยู่แล้ว — ระบบจะจัดการทุกอย่างให้

### ✨ ฟีเจอร์หลัก

| ฟีเจอร์ | รายละเอียด |
|---|---|
| 🎙️ **ถอดความเสียง** | รองรับ `.mp3` และ `.wav` ผ่าน Groq API (cloud) หรือ Faster-Whisper (CPU) |
| ▶️ **YouTube** | วาง URL → ดาวน์โหลดเสียงอัตโนมัติ → ถอดความ → สรุป |
| 📝 **วางข้อความ** | สรุป transcript ที่มีอยู่แล้วได้ทันที |
| 🤖 **สรุปด้วย LLM** | รองรับ OpenRouter และ Google Gemini |
| 📋 **6 รูปแบบสรุป** | รายงานราชการ / สรุปย่อ / วิเคราะห์การเมือง / มติ / วิเคราะห์ผู้พูด / แถลงข่าว |
| 💾 **Export** | ดาวน์โหลดรายงานเป็น `.txt` และ `.docx` |
| 🎨 **Parliament Dark Gold UI** | ธีมสีทอง-น้ำเงินเข้ม สไตล์สถาบันนิติบัญญัติ |

### 📁 โครงสร้างโปรเจกต์

```
parliament-transcriber/
├── app.py                  ← Streamlit app หลัก
├── style.css               ← ธีม Parliament Dark Gold
├── requirements.txt        ← Python dependencies
├── .env                    ← API Keys (ห้าม commit ขึ้น Git)
├── .gitignore
└── utils/
    ├── transcriber.py      ← Groq Whisper API + Local Faster-Whisper
    ├── summarizer.py       ← Prompt templates + OpenRouter/Gemini
    └── exporter.py         ← Export .txt และ .docx
```

### 🚀 การติดตั้งและรัน

**1. ติดตั้ง FFmpeg**

```bash
# Ubuntu / Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
winget install Gyan.FFmpeg
```

**2. Clone และติดตั้ง dependencies**

```bash
git clone https://github.com/your-username/parliament-transcriber.git
cd parliament-transcriber

python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

pip install -r requirements.txt
pip install groq yt-dlp python-dotenv
```

**3. ตั้งค่า API Keys**

สร้างไฟล์ `.env` ในโฟลเดอร์โปรเจกต์:

```env
# Groq API — ถอดความเสียง (ฟรี)
# สมัครที่: https://console.groq.com
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx

# OpenRouter — สรุปด้วย LLM (ฟรีบางโมเดล)
# สมัครที่: https://openrouter.ai/keys
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx

# Google Gemini — ทางเลือก (ถ้ามี)
# สมัครที่: https://aistudio.google.com/apikey
GEMINI_API_KEY=AIza-xxxxxxxxxxxx
```

**4. รันแอป**

```bash
streamlit run app.py
```

เปิดเบราว์เซอร์ที่ `http://localhost:8501`

### ⚙️ การตั้งค่าใน Sidebar

**Speech-to-Text Engine**

| Engine | ความเร็ว | ต้องการ Internet | หมายเหตุ |
|---|---|---|---|
| **Groq API** ⭐ | ⚡⚡⚡⚡⚡ | ใช่ | ฟรี — เร็วกว่า CPU 10–50x |
| **Local Whisper** | ⚡⚡ | ไม่ | Privacy สูงกว่า แต่ช้ากว่า |

**โมเดล Groq ที่แนะนำ:** `whisper-large-v3-turbo`

**LLM Provider**

| Provider | โมเดลที่แนะนำ | ฟรี |
|---|---|---|
| **OpenRouter** | `google/gemini-2.0-flash-001` | ✅ |
| **Google Gemini** | `gemini-2.0-flash` | ✅ (ถ้าไม่ผูก Billing) |

**รูปแบบสรุป**

| รูปแบบ | เหมาะสำหรับ |
|---|---|
| 📋 รายงานการประชุมสมบูรณ์ | งานราชการ เอกสารทางการ |
| ⚡ สรุปย่อประเด็นสำคัญ | ผู้บริหาร สื่อมวลชน |
| 🏛️ วิเคราะห์การเมือง | นักวิชาการ นักวิเคราะห์ |
| ✅ มติและ Action Items | ฝ่ายบริหาร ติดตามงาน |
| 🎤 วิเคราะห์ผู้อภิปราย | นักข่าว นักวิจัย |
| 📰 แถลงการณ์สื่อมวลชน | PR ประชาสัมพันธ์ |

### 📊 ประมาณเวลาประมวลผล

| ความยาวไฟล์ | Groq API | Local Whisper (small) |
|---|---|---|
| 10 นาที | ~15–30 วินาที | ~8 นาที |
| 30 นาที | ~45–90 วินาที | ~25 นาที |
| 60 นาที | ~2–3 นาที | ~50 นาที |
| 120 นาที | ~4–6 นาที | ~100 นาที |

> ไฟล์ใหญ่กว่า 25 MB ระบบจะแบ่ง chunk อัตโนมัติ

### 🐛 ปัญหาที่พบบ่อย

| ปัญหา | วิธีแก้ |
|---|---|
| `FFmpeg not found` | ติดตั้ง FFmpeg และเพิ่มใน PATH |
| `Groq 413 File Too Large` | ติดตั้ง pydub: `pip install pydub` |
| `OpenRouter 429` | ถึง rate limit — รอสักครู่หรือเปลี่ยนโมเดล |
| `latin-1 codec error` | อัปเดตเป็น `summarizer.py` ล่าสุด |
| Sidebar widgets หาย | อัปเดตเป็น `app.py` ล่าสุด |

### 🔒 ความปลอดภัย

- API Keys เก็บใน `.env` — **ห้าม commit ขึ้น Git เด็ดขาด**
- ไฟล์เสียงที่อัปโหลดจะถูกลบออกหลังประมวลผลอัตโนมัติ
- ไม่มีการเก็บข้อมูลถาวรในระบบ

### 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | [Streamlit](https://streamlit.io) |
| STT (Cloud) | [Groq Whisper API](https://console.groq.com) |
| STT (Local) | [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) |
| LLM | [OpenRouter](https://openrouter.ai) / [Google Gemini](https://aistudio.google.com) |
| YouTube | [yt-dlp](https://github.com/yt-dlp/yt-dlp) |
| Audio | [FFmpeg](https://ffmpeg.org) / [pydub](https://github.com/jiaaro/pydub) |
| Export | [python-docx](https://python-docx.readthedocs.io) |
| Styling | Custom CSS — Parliament Dark Gold |

### 📄 License

MIT License — ใช้งานได้อิสระ ทั้งส่วนตัวและองค์กร

</details>

---

<div align="center">
  <sub>Built with ❤️ for Thai Democracy &nbsp;·&nbsp; 🏛️ Parliament AI</sub>
</div>