# 🏛️ Parliament AI
### Thai Legislative Transcription & Summarization System

> ระบบถอดความและสรุปการประชุมรัฐสภาไทย อัตโนมัติด้วย AI  
> รองรับไฟล์เสียง · ลิงก์ YouTube · วางข้อความ

---

## ✨ ฟีเจอร์หลัก

| ฟีเจอร์ | รายละเอียด |
|---|---|
| 🎙️ **ถอดความเสียง** | รองรับ `.mp3` และ `.wav` ด้วย Groq API (cloud) หรือ Faster-Whisper (local CPU) |
| ▶️ **YouTube** | วาง URL → ดาวน์โหลดเสียงอัตโนมัติ → ถอดความ → สรุป |
| 📝 **วางข้อความ** | สรุป transcript ที่มีอยู่แล้วได้ทันที |
| 🤖 **สรุปด้วย LLM** | รองรับ OpenRouter และ Google Gemini |
| 📋 **6 รูปแบบสรุป** | รายงานราชการ / สรุปย่อ / วิเคราะห์การเมือง / มติ / วิเคราะห์ผู้พูด / แถลงข่าว |
| 💾 **Export** | ดาวน์โหลดรายงานเป็น `.txt` และ `.docx` |
| 🎨 **Parliament Dark Gold UI** | ธีมสีทอง-น้ำเงินเข้ม สไตล์สถาบันนิติบัญญัติ |

---

## 📁 โครงสร้างโปรเจกต์

```
parliament-transcriber/
├── app.py                  ← Streamlit app หลัก
├── style.css               ← ธีม Parliament Dark Gold
├── requirements.txt        ← Python dependencies
├── .env                    ← API Keys (ไม่ commit ขึ้น Git)
├── .gitignore
└── utils/
    ├── transcriber.py      ← Groq Whisper API + Local Faster-Whisper
    ├── summarizer.py       ← Prompt templates + OpenRouter/Gemini calls
    └── exporter.py         ← Export .txt และ .docx
```

---

## 🚀 การติดตั้งและรัน

### 1. ติดตั้ง FFmpeg

```bash
# Ubuntu / Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
winget install Gyan.FFmpeg
```

### 2. Clone และติดตั้ง dependencies

```bash
git clone https://github.com/your-username/parliament-transcriber.git
cd parliament-transcriber

python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

pip install -r requirements.txt
pip install groq yt-dlp python-dotenv
```

### 3. ตั้งค่า API Keys

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

### 4. รันแอป

```bash
streamlit run app.py
```

เปิดเบราว์เซอร์ที่ `http://localhost:8501`

---

## ⚙️ การตั้งค่าใน Sidebar

### 🎙️ Speech-to-Text Engine

| Engine | ความเร็ว | ต้องการ Internet | หมายเหตุ |
|---|---|---|---|
| **Groq API** (แนะนำ) | ⚡⚡⚡⚡⚡ | ✅ ใช่ | ฟรี — เร็วกว่า CPU 10–50x |
| **Local Whisper** | ⚡⚡ | ❌ ไม่ | Privacy สูง แต่ช้ากว่า |

**โมเดล Groq ที่แนะนำ:** `whisper-large-v3-turbo`

### 🤖 LLM Provider

| Provider | โมเดลที่แนะนำ | ฟรี |
|---|---|---|
| **OpenRouter** | `google/gemini-2.0-flash-001` | ✅ |
| **Google Gemini** | `gemini-2.0-flash` | ✅ (ถ้าไม่ผูก Billing) |

### 📋 รูปแบบสรุป

| รูปแบบ | เหมาะสำหรับ |
|---|---|
| 📋 รายงานการประชุมสมบูรณ์ | งานราชการ เอกสารทางการ |
| ⚡ สรุปย่อประเด็นสำคัญ | ผู้บริหาร สื่อมวลชน |
| 🏛️ วิเคราะห์การเมือง | นักวิชาการ นักวิเคราะห์ |
| ✅ มติและ Action Items | ฝ่ายบริหาร ติดตามงาน |
| 🎤 วิเคราะห์ผู้อภิปราย | นักข่าว นักวิจัย |
| 📰 แถลงการณ์สื่อมวลชน | PR ประชาสัมพันธ์ |

---

## 📊 ประมาณเวลาประมวลผล

| ความยาวไฟล์ | Groq API | Local Whisper (small) |
|---|---|---|
| 10 นาที | ~15–30 วินาที | ~8 นาที |
| 30 นาที | ~45–90 วินาที | ~25 นาที |
| 60 นาที | ~2–3 นาที | ~50 นาที |
| 120 นาที | ~4–6 นาที | ~100 นาที |

> **หมายเหตุ:** Groq มี limit ไฟล์สูงสุด 25 MB ต่อครั้ง — ไฟล์ใหญ่กว่านั้นระบบจะแบ่ง chunk อัตโนมัติ

---

## 🔑 API Keys และ Rate Limits

### Groq (Speech-to-Text)
- สมัครฟรีที่ [console.groq.com](https://console.groq.com)
- ไม่ต้องใส่บัตรเครดิต
- ดู limit จริงที่ [console.groq.com/settings/limits](https://console.groq.com/settings/limits)

### OpenRouter (LLM)
- สมัครฟรีที่ [openrouter.ai](https://openrouter.ai/keys)
- โมเดลฟรีที่แนะนำ: `google/gemini-2.0-flash-001`, `meta-llama/llama-3.3-70b-instruct`

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | [Streamlit](https://streamlit.io) |
| Speech-to-Text (Cloud) | [Groq Whisper API](https://console.groq.com) |
| Speech-to-Text (Local) | [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) |
| LLM Summarization | [OpenRouter](https://openrouter.ai) / [Google Gemini](https://aistudio.google.com) |
| YouTube Download | [yt-dlp](https://github.com/yt-dlp/yt-dlp) |
| Audio Processing | [FFmpeg](https://ffmpeg.org) / [pydub](https://github.com/jiaaro/pydub) |
| Document Export | [python-docx](https://python-docx.readthedocs.io) |
| Styling | Custom CSS — Parliament Dark Gold Theme |

---

## 🔒 ความปลอดภัย

- API Keys เก็บใน `.env` — **ห้าม commit ขึ้น Git**
- ไฟล์ `.gitignore` ครอบคลุม `.env`, `venv/`, `__pycache__/` แล้ว
- ไฟล์เสียงที่อัปโหลดจะถูกลบออกหลังประมวลผลอัตโนมัติ
- ข้อมูลไม่ถูกเก็บถาวรในระบบ

---

## 🐛 ปัญหาที่พบบ่อย

**FFmpeg not found**
```bash
# ตรวจสอบว่าติดตั้งแล้ว
ffmpeg -version
# ถ้าไม่พบให้ติดตั้งตาม OS ด้านบน
```

**Groq API 413 File Too Large**
> ระบบจะแบ่งไฟล์อัตโนมัติ — ถ้ายังเกิด error ให้ติดตั้ง pydub: `pip install pydub`

**OpenRouter 429 Too Many Requests**
> ถึง rate limit แล้ว รอสักครู่แล้วลองใหม่ หรือเปลี่ยนโมเดลเป็นตัวอื่น

**Sidebar widgets หายหลัง collapse**
> อัปเดตเป็นไฟล์ `app.py` ล่าสุด — แก้แล้วด้วยการใส่ `key=` ให้ทุก widget

---

## 📄 License

MIT License — ใช้งานได้อิสระ ทั้งส่วนตัวและองค์กร

---

<div align="center">
  <sub>Built with ❤️ for Thai Democracy · Parliament AI</sub>
</div>
