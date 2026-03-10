"""
utils/transcriber.py
──────────────────────────────────────────────────────────────────────────────
รองรับ 2 engine:
  • LOCAL  — Faster-Whisper (ทำงานบน CPU เครื่องตัวเอง)
  • GROQ   — Groq Whisper API (Cloud GPU เร็วกว่า 10–50x)

ทั้งคู่ใช้ interface เดียวกัน:
  transcribe_audio(...) → Generator[tuple[str, float, str]]
  yields: (new_text, progress_0_to_1, status_message)
"""

import os
import time
from pathlib import Path
from typing import Generator, Tuple

# ── Thai parliament vocabulary hint ────────────────────────────────────────────
THAI_PARLIAMENT_PROMPT = (
    "การประชุมสภาผู้แทนราษฎร วุฒิสภา คณะกรรมาธิการ ประธานสภา รองประธาน "
    "สมาชิกสภาผู้แทนราษฎร ญัตติ ร่างพระราชบัญญัติ พระราชบัญญัติ งบประมาณ "
    "กระทรวง กรม เสนอ อภิปราย ลงมติ เห็นด้วย ไม่เห็นด้วย งดออกเสียง "
    "รัฐมนตรี นายกรัฐมนตรี โครงการ นโยบาย ประชาชน"
)

# ── STT Engine catalogue ───────────────────────────────────────────────────────
STT_ENGINES: dict[str, dict] = {
    "groq": {
        "label": "⚡ Groq API (Cloud) — เร็วกว่า 10–50x แนะนำ",
        "desc": "ใช้ Whisper large-v3 บน Groq GPU cloud — ฟรี รับ Key ที่ console.groq.com",
        "placeholder": "gsk_...",
        "needs_key": True,
    },
    "local": {
        "label": "💻 Local Whisper (CPU) — ไม่ต้องใช้ Internet",
        "desc": "ทำงานบนเครื่องตัวเอง ช้ากว่าแต่ Privacy สูงกว่า",
        "placeholder": "",
        "needs_key": False,
    },
}

# ── Local Whisper model catalogue ──────────────────────────────────────────────
WHISPER_MODELS: dict[str, dict] = {
    "tiny": {
        "label": "⚡ Tiny  (~75 MB)  — เร็วมาก แต่แม่นน้อย",
        "desc": "เหมาะสำหรับทดสอบเบื้องต้น หรือ CPU ช้ามาก",
    },
    "base": {
        "label": "🔹 Base  (~150 MB) — สมดุลดีสำหรับ CPU",
        "desc": "แนะนำสำหรับเครื่อง CPU ที่มี RAM < 8 GB",
    },
    "small": {
        "label": "🔶 Small (~500 MB) — แม่นยำพอสมควร (แนะนำ)",
        "desc": "ค่า default ที่ดีที่สุดสำหรับงานราชการภาษาไทย",
    },
    "medium": {
        "label": "🔷 Medium (~1.5 GB) — แม่นยำสูง",
        "desc": "ต้องการ RAM ≥ 8 GB และใช้เวลานานขึ้น",
    },
    "large-v3-turbo": {
        "label": "🏆 Large-v3-turbo (~800 MB) — แม่นยำสูงสุด",
        "desc": "แนะนำถ้ามี RAM ≥ 12 GB",
    },
}

# ── Groq models ────────────────────────────────────────────────────────────────
GROQ_MODELS: dict[str, dict] = {
    "whisper-large-v3-turbo": {
        "label": "🏆 Whisper Large-v3-turbo — เร็ว + แม่น (แนะนำ)",
        "desc": "ดีที่สุดสำหรับภาษาไทย บน Groq cloud",
    },
    "whisper-large-v3": {
        "label": "🔷 Whisper Large-v3 — แม่นสูงสุด",
        "desc": "แม่นกว่า turbo เล็กน้อย แต่ช้ากว่าเล็กน้อย",
    },
    "distil-whisper-large-v3-en": {
        "label": "⚡ Distil Whisper — เร็วที่สุด (อังกฤษเท่านั้น)",
        "desc": "ไม่แนะนำสำหรับภาษาไทย",
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════


def transcribe_audio(
    audio_path: str,
    engine: str = "groq",
    groq_api_key: str = "",
    groq_model: str = "whisper-large-v3-turbo",
    model_size: str = "small",
    beam_size: int = 2,
    vad_filter: bool = True,
    chunk_minutes: int = 5,
) -> Generator[Tuple[str, float, str], None, None]:
    """
    Unified transcription generator.
    Yields: (new_text_chunk, progress_float, status_string)
    """
    if engine == "groq":
        yield from _transcribe_groq(audio_path, groq_api_key, groq_model)
    else:
        yield from _transcribe_local(audio_path, model_size, beam_size, vad_filter)


# ══════════════════════════════════════════════════════════════════════════════
# GROQ ENGINE
# ══════════════════════════════════════════════════════════════════════════════

_GROQ_MAX_BYTES = 25 * 1024 * 1024  # 25 MB — Groq file size limit


def _transcribe_groq(
    audio_path: str,
    api_key: str,
    model: str,
) -> Generator[Tuple[str, float, str], None, None]:
    """
    ส่งไฟล์ไปถอดความที่ Groq API
    ถ้าไฟล์ > 25 MB จะแบ่งก่อนอัตโนมัติด้วย pydub
    """
    try:
        from groq import Groq
    except ImportError:
        raise ImportError("กรุณาติดตั้ง groq:  pip install groq")

    yield ("", 0.05, "🔗 กำลังเชื่อมต่อ Groq API…")

    client = Groq(api_key=api_key)
    file_size = os.path.getsize(audio_path)

    if file_size <= _GROQ_MAX_BYTES:
        # ── ไฟล์เล็ก: ส่งตรงได้เลย ─────────────────────────────────
        yield ("", 0.10, "📤 กำลังอัปโหลดและถอดความ…")
        result = _groq_call(client, audio_path, model)
        yield (result, 1.0, "✅ ถอดความเสร็จสิ้น")

    else:
        # ── ไฟล์ใหญ่: แบ่ง chunk ─────────────────────────────────────
        yield ("", 0.05, "✂️ ไฟล์ใหญ่กว่า 25 MB — กำลังแบ่งไฟล์…")
        chunks = _split_audio(audio_path)
        total = len(chunks)

        full_text = ""
        for i, chunk_path in enumerate(chunks):
            pct = 0.10 + 0.85 * (i / total)
            status = f"📤 กำลังถอดความ chunk {i+1}/{total}…"
            yield ("", pct, status)

            try:
                text = _groq_call(client, chunk_path, model)
                full_text += text + "\n"
                yield (text + "\n", pct, status)
            finally:
                try:
                    os.unlink(chunk_path)
                except Exception:
                    pass

        yield ("", 1.0, "✅ ถอดความเสร็จสิ้น")


def _groq_call(client, audio_path: str, model: str) -> str:
    """เรียก Groq transcription API และคืนข้อความ"""
    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(
            file=(Path(audio_path).name, f),
            model=model,
            language="th",
            prompt=THAI_PARLIAMENT_PROMPT,
            response_format="verbose_json",  # ได้ segments + timestamps
            timestamp_granularities=["segment"],
        )

    # แปลง segments → timestamp lines
    lines = []
    if hasattr(result, "segments") and result.segments:
        for seg in result.segments:
            ts = _fmt_ts(seg.get("start", 0) if isinstance(seg, dict) else seg.start)
            text = (seg.get("text", "") if isinstance(seg, dict) else seg.text).strip()
            if text:
                lines.append(f"{ts} {text}")
    else:
        lines.append(result.text or "")

    return "\n".join(lines)


def _split_audio(audio_path: str, chunk_ms: int = 10 * 60 * 1000) -> list[str]:
    """แบ่งไฟล์เสียงเป็น chunks ด้วย pydub (10 นาที/chunk)"""
    try:
        from pydub import AudioSegment
    except ImportError:
        raise ImportError("กรุณาติดตั้ง pydub:  pip install pydub")

    audio = AudioSegment.from_file(audio_path)
    chunks = []
    for start in range(0, len(audio), chunk_ms):
        chunk = audio[start : start + chunk_ms]
        out_path = audio_path + f"_chunk_{start}.mp3"
        chunk.export(out_path, format="mp3")
        chunks.append(out_path)
    return chunks


# ══════════════════════════════════════════════════════════════════════════════
# LOCAL WHISPER ENGINE
# ══════════════════════════════════════════════════════════════════════════════


def _transcribe_local(
    audio_path: str,
    model_size: str,
    beam_size: int,
    vad_filter: bool,
) -> Generator[Tuple[str, float, str], None, None]:
    """Faster-Whisper บน CPU พร้อม int8 optimization"""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise ImportError("กรุณาติดตั้ง faster-whisper:  pip install faster-whisper")

    yield ("", 0.02, f"💻 กำลังโหลดโมเดล {model_size}…")

    cpu_threads = max(4, os.cpu_count() or 4)
    model = WhisperModel(
        model_size,
        device="cpu",
        compute_type="int8",
        cpu_threads=cpu_threads,
        num_workers=1,
    )

    # ประมาณ duration
    duration = _get_duration(audio_path)
    yield ("", 0.05, "กำลังถอดความ…")

    segments, _ = model.transcribe(
        audio_path,
        language="th",
        beam_size=beam_size,
        best_of=2,
        vad_filter=vad_filter,
        vad_parameters={"min_silence_duration_ms": 500},
        initial_prompt=THAI_PARLIAMENT_PROMPT,
        word_timestamps=False,
        condition_on_previous_text=True,
    )

    buf = ""
    last_yield = time.time()

    for seg in segments:
        ts = _fmt_ts(seg.start)
        line = f"{ts} {seg.text.strip()}\n"
        buf += line

        pct = min(0.05 + 0.90 * (seg.end / duration), 0.95) if duration else 0.5

        if (time.time() - last_yield > 1.0) or len(buf) > 500:
            yield (buf, pct, f"กำลังถอดความ… {_fmt_ts(seg.start)}")
            buf = ""
            last_yield = time.time()

    if buf:
        yield (buf, 0.97, "กำลังเสร็จสิ้น…")
    yield ("", 1.0, "✅ ถอดความเสร็จสิ้น")


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════


def _fmt_ts(seconds: float) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"[{h:02d}:{m:02d}:{s:02d}]" if h else f"[{m:02d}:{s:02d}]"


def _get_duration(audio_path: str) -> float | None:
    try:
        import subprocess, json

        p = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                audio_path,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return float(json.loads(p.stdout)["format"]["duration"])
    except Exception:
        return None
