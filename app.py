"""
Transcript AI — Transcription & Summarization System
"""

import streamlit as st
import tempfile
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Transcript AI",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from utils.transcriber import transcribe_audio, WHISPER_MODELS, STT_ENGINES, GROQ_MODELS
from utils.summarizer import summarize_transcript, SUMMARY_MODES, PROVIDERS
from utils.exporter import export_txt, export_docx
from utils.database import (
    init_db,
    save_result,
    get_all,
    get_by_id,
    delete_by_id,
    search,
    get_stats,
)

init_db()


# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
def _load_css(path="style.css"):
    f = Path(__file__).parent / path
    if f.exists():
        st.markdown(
            f"<style>{f.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True
        )


_load_css()

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
for k, v in {
    "active_dialog": None,  # None | "result" | "settings" | "history"
    "pending_pipeline": None,  # {"path":..., "label":...} รอหลัง settings save
    "history_view_id": None,
    "transcript": "",
    "summary": "",
    "source_name": "output",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════════════
def _cfg(key, default):
    if key not in st.session_state:
        st.session_state[key] = default
    return st.session_state[key]


_prov_default = list(PROVIDERS.keys())[0]
stt_engine = _cfg("sb_stt_engine", list(STT_ENGINES.keys())[0])
groq_key = _cfg("sb_groq_key", os.getenv("GROQ_API_KEY", ""))
groq_model = _cfg("sb_groq_model", list(GROQ_MODELS.keys())[0])
whisper_model = _cfg("sb_whisper_model", "small")
selected_provider = _cfg("sb_provider", _prov_default)
api_key = _cfg(
    "sb_llm_key", os.getenv("OPENROUTER_API_KEY", "") or os.getenv("GROQ_API_KEY", "")
)
llm_model = _cfg("sb_llm_model", PROVIDERS[_prov_default]["models"][0])
summary_mode = _cfg("sb_summary_mode", list(SUMMARY_MODES.keys())[0])
beam_size = _cfg("sb_beam", 2)
vad_filter = _cfg("sb_vad", True)
chunk_minutes = _cfg("sb_chunk", 5)

# sync จาก session_state
stt_engine = st.session_state.get("sb_stt_engine", stt_engine)
groq_key = st.session_state.get("sb_groq_key", groq_key)
groq_model = st.session_state.get("sb_groq_model", groq_model)
whisper_model = st.session_state.get("sb_whisper_model", whisper_model)
selected_provider = st.session_state.get("sb_provider", selected_provider)
api_key = st.session_state.get("sb_llm_key", api_key)
llm_model = st.session_state.get("sb_llm_model", llm_model)
summary_mode = st.session_state.get("sb_summary_mode", summary_mode)
beam_size = st.session_state.get("sb_beam", beam_size)
vad_filter = st.session_state.get("sb_vad", vad_filter)
chunk_minutes = st.session_state.get("sb_chunk", chunk_minutes)


# ══════════════════════════════════════════════════════════════════════════════
# MODAL CONTENT FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════


# ── Result ────────────────────────────────────────────────────────────────────
def _render_result():
    import json as _json

    transcript = st.session_state.get("transcript", "")
    summary = st.session_state.get("summary", "")
    source_name = st.session_state.get("source_name", "output")
    score = st.session_state.get("quality_score", 0)
    stem = Path(source_name).stem

    # ── Quality Score bar ─────────────────────────────────
    if score:
        dots_filled = "●" * score
        dots_empty = "○" * (5 - score)
        label_map = {1: "Low", 2: "Fair", 3: "Good", 4: "High", 5: "Excellent"}
        score_label = label_map.get(score, "—")
        color_map = {
            1: "#c0392b",
            2: "#e67e22",
            3: "#f0913a",
            4: "#52b788",
            5: "#27ae60",
        }
        score_color = color_map.get(score, "#888")
        st.markdown(
            f'<div class="quality-bar">'
            + f'<span class="quality-label">Quality</span>'
            + f'<span class="quality-dots" style="color:{score_color}">{dots_filled}</span>'
            + f'<span class="quality-dots-empty">{dots_empty}</span>'
            + f'<span class="quality-score-text" style="color:{score_color}">{score_label}</span>'
            + "</div>",
            unsafe_allow_html=True,
        )

    # meta
    proc_time = st.session_state.get("last_process_time", "")
    meta = source_name + (f"  ·  ⏱ {proc_time}" if proc_time else "")
    st.caption(meta)

    # keywords
    def _kws(text, n=15):
        import re

        stops = {
            "และ",
            "ที่",
            "ใน",
            "การ",
            "ของ",
            "มี",
            "ได้",
            "ให้",
            "เพื่อ",
            "โดย",
            "จาก",
            "แต่",
            "หรือ",
            "เป็น",
            "กับ",
            "ว่า",
            "นี้",
            "จะ",
            "ซึ่ง",
            "ไม่",
            "ต้อง",
            "ควร",
            "อยู่",
            "ยัง",
            "แล้ว",
            "the",
            "a",
            "an",
            "of",
            "in",
            "to",
            "and",
            "is",
            "are",
            "was",
            "were",
            "for",
            "with",
            "that",
            "this",
            "it",
            "be",
            "by",
            "on",
            "at",
            "or",
            "from",
            "not",
            "but",
            "have",
            "has",
            "will",
            "can",
            "all",
            "also",
            "its",
            "as",
            "been",
        }
        words = re.findall(r"[ก-๙a-zA-Z]{3,}", text)
        freq = {}
        for w in words:
            wl = w.lower()
            if wl not in stops:
                freq[wl] = freq.get(wl, 0) + 1
        return [w for w, _ in sorted(freq.items(), key=lambda x: -x[1])[:n]]

    kws = _kws(summary)
    if kws:
        st.markdown('<p class="section-label">Keywords</p>', unsafe_allow_html=True)
        chips = " ".join(f'<span class="kw-chip">{k}</span>' for k in kws)
        st.markdown(f'<div class="kw-wrap">{chips}</div>', unsafe_allow_html=True)

    st.markdown('<p class="section-label">Summary</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)

    # ── Copy to clipboard button ───────────────────────────
    copy_js = summary.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    copy_html = (
        '<button class="copy-btn" '
        + 'onclick="navigator.clipboard.writeText(`'
        + copy_js
        + "`)"
        + '.then(()=>{this.textContent=&quot;Copied!&quot;;setTimeout(()=>this.textContent=&quot;Copy&quot;,1500)})">'
        + "Copy</button>"
    )
    st.markdown(copy_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("Full Transcript", expanded=False):
        # colorize timestamps
        import re as _re

        html_lines = []
        for line in transcript.split("\n"):
            m = _re.match(r"^(\[\d{2}:\d{2}(?::\d{2})?\])(.*)", line)
            if m:
                html_lines.append(
                    f'<span class="ts-stamp">{m.group(1)}</span>'
                    + f'<span class="ts-text">{m.group(2)}</span>'
                )
            else:
                html_lines.append(line)
        st.markdown(
            f'<div class="transcript-box">{"<br>".join(html_lines)}</div>',
            unsafe_allow_html=True,
        )

    # ── Export row 1: existing formats ────────────────────
    st.markdown(
        '<p class="section-label" style="margin-top:1.2rem">Download</p>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            "📄 Summary .txt",
            data=export_txt(transcript, summary),
            file_name=f"{stem}_summary.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_txt_modal",
        )
    with c2:
        try:
            st.download_button(
                "📝 Report .docx",
                data=export_docx(transcript, summary),
                file_name=f"{stem}_report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                key="dl_docx_modal",
            )
        except Exception as e:
            st.caption(f"DOCX: {e}")
    with c3:
        st.download_button(
            "📜 Transcript .txt",
            data=transcript.encode("utf-8"),
            file_name=f"{stem}_transcript.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_tr_modal",
        )

    # ── Export row 2: new formats ─────────────────────────
    st.markdown(
        '<p class="section-label" style="margin-top:0.6rem">More Formats</p>',
        unsafe_allow_html=True,
    )
    d1, d2, d3 = st.columns(3)
    with d1:
        md_content = f"# Summary\n\n{summary}\n\n---\n\n# Transcript\n\n{transcript}"
        st.download_button(
            "📋 Markdown .md",
            data=md_content.encode("utf-8"),
            file_name=f"{stem}_report.md",
            mime="text/markdown",
            use_container_width=True,
            key="dl_md_modal",
        )
    with d2:
        json_data = _json.dumps(
            {
                "source": source_name,
                "summary": summary,
                "transcript": transcript,
            },
            ensure_ascii=False,
            indent=2,
        )
        st.download_button(
            "🔧 JSON .json",
            data=json_data.encode("utf-8"),
            file_name=f"{stem}_data.json",
            mime="application/json",
            use_container_width=True,
            key="dl_json_modal",
        )
    with d3:
        srt_lines = []
        import re as _re2

        for i, line in enumerate(transcript.split("\n"), 1):
            m = _re2.match(r"\[(\d{2}:\d{2})\](.*)", line.strip())
            if m:
                ts, txt = m.group(1), m.group(2).strip()
                srt_lines.append(f"{i}\n00:{ts},000 --> 00:{ts},999\n{txt}\n")
        srt_data = "\n".join(srt_lines) if srt_lines else transcript
        st.download_button(
            "🎬 Subtitle .srt",
            data=srt_data.encode("utf-8"),
            file_name=f"{stem}.srt",
            mime="text/plain",
            use_container_width=True,
            key="dl_srt_modal",
        )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✕  Close", key="close_result_modal"):
        st.session_state["active_dialog"] = None
        st.rerun()


# ── Settings ──────────────────────────────────────────────────────────────────
def _render_settings():
    prov = list(PROVIDERS.keys())[0]  # openrouter เท่านั้น

    st.markdown("#### 🎙️ Speech-to-Text")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        eng = st.selectbox(
            "Engine",
            key="sb_stt_engine",
            options=list(STT_ENGINES.keys()),
            format_func=lambda k: STT_ENGINES[k]["label"],
        )
        st.caption(STT_ENGINES[eng]["desc"])

        if eng == "groq":
            gk = st.text_input(
                "Groq API Key",
                key="sb_groq_key",
                type="password",
                value=st.session_state.get(
                    "sb_groq_key", os.getenv("GROQ_API_KEY", "")
                ),
                placeholder="gsk_...",
            )
            if gk:
                st.success("⚡ Groq connected")
            else:
                st.warning("Add key or set GROQ_API_KEY in .env")
            st.selectbox(
                "Groq Model",
                key="sb_groq_model",
                options=list(GROQ_MODELS.keys()),
                format_func=lambda k: GROQ_MODELS[k]["label"],
            )
        else:
            st.selectbox(
                "Whisper Model",
                key="sb_whisper_model",
                options=list(WHISPER_MODELS.keys()),
                index=2,
                format_func=lambda k: WHISPER_MODELS[k]["label"],
            )

    with c2:
        st.markdown("**🔧 Advanced**")
        st.slider("Beam Size", 1, 5, 2, key="sb_beam")
        st.checkbox("VAD Filter (cut silence)", value=True, key="sb_vad")
        st.slider("Chunk Size (min)", 1, 10, 5, key="sb_chunk")

    st.markdown("---")
    st.markdown("#### 🤖 Language Model — OpenRouter")

    lk = st.text_input(
        "OpenRouter API Key",
        key="sb_llm_key",
        type="password",
        value=st.session_state.get("sb_llm_key", os.getenv("OPENROUTER_API_KEY", "")),
        placeholder="sk-or-v1-...",
        help="Get your free key at openrouter.ai/keys",
    )

    col_status, col_link = st.columns([2, 1])
    with col_status:
        if lk:
            st.success("🔑 API Key ready")
        else:
            st.warning("API Key required to summarize")
    with col_link:
        st.markdown("[Get free key →](https://openrouter.ai/keys)")

    # ซ่อน provider key ไว้ใน session (openrouter เท่านั้น)
    st.session_state["sb_provider"] = prov

    st.markdown("**Select Model**")
    st.selectbox(
        "Model",
        key="sb_llm_model",
        options=PROVIDERS[prov]["models"],
        help="Recommended: google/gemini-2.0-flash-001 (free)",
    )

    st.markdown("---")
    st.markdown("#### 📋 Summary Format")
    st.selectbox(
        "Format",
        key="sb_summary_mode",
        options=list(SUMMARY_MODES.keys()),
        format_func=lambda k: SUMMARY_MODES[k]["label"],
    )
    st.caption(
        SUMMARY_MODES[
            st.session_state.get("sb_summary_mode", list(SUMMARY_MODES.keys())[0])
        ]["desc"]
    )

    st.markdown("---")

    # ปุ่ม Save
    pending = st.session_state.get("pending_pipeline")
    btn_label = "▶  Save & Start Transcription" if pending else "Save & Close"
    btn_type = "primary" if pending else "secondary"

    if not lk:
        st.error("Please enter your OpenRouter API Key before continuing.")

    save_col, cancel_col = st.columns([2, 1])
    with save_col:
        if st.button(
            btn_label,
            type="primary",
            use_container_width=True,
            key="settings_save",
            disabled=not lk,
        ):
            st.session_state["active_dialog"] = None
            # ถ้ามี pending pipeline รอ ให้ flag ว่าพร้อมรัน
            if pending:
                st.session_state["run_pipeline_now"] = True
            st.rerun()
    with cancel_col:
        if st.button("Cancel", use_container_width=True, key="settings_cancel"):
            st.session_state["active_dialog"] = None
            st.session_state["pending_pipeline"] = None
            st.rerun()


# ── History Detail ────────────────────────────────────────────────────────────
def _render_history_detail():
    rid = st.session_state.get("history_view_id")
    rec = get_by_id(rid)
    if not rec:
        st.error("Record not found")
        return

    name = rec["source_name"]
    stem = Path(name).stem
    tr = rec["transcript"] or ""
    smm = rec["summary"] or ""

    st.markdown(
        f"**{name}**  "
        f"<span style='font-size:.8rem;color:var(--text-muted,#b07040)'>"
        f"{rec['created_at']} &nbsp;·&nbsp; {rec['source_type']} &nbsp;·&nbsp; "
        f"{rec.get('llm_model','')}</span>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    st.markdown('<p class="section-label">Summary</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="summary-box">{smm}</div>', unsafe_allow_html=True)

    with st.expander("Full Transcript", expanded=False):
        st.text_area(
            "Transcript",
            tr,
            height=300,
            label_visibility="collapsed",
            key="hist_tr_view",
        )

    st.markdown("---")
    dc1, dc2, dc3 = st.columns(3)
    with dc1:
        st.download_button(
            "📄 Summary .txt",
            data=export_txt(tr, smm),
            file_name=f"{stem}_summary.txt",
            mime="text/plain",
            use_container_width=True,
            key="hist_dl_txt",
        )
    with dc2:
        try:
            st.download_button(
                "📝 Report .docx",
                data=export_docx(tr, smm),
                file_name=f"{stem}_report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                key="hist_dl_docx",
            )
        except Exception as ex:
            st.caption(f"DOCX: {ex}")
    with dc3:
        st.download_button(
            "📜 Transcript .txt",
            data=tr.encode("utf-8"),
            file_name=f"{stem}_transcript.txt",
            mime="text/plain",
            use_container_width=True,
            key="hist_dl_tr",
        )

    # Tags editor
    st.markdown("---")
    st.markdown('<p class="section-label">Tags</p>', unsafe_allow_html=True)
    from utils.database import update_tags as _update_tags

    _existing = []
    try:
        _existing = _json.loads(rec.get("tags", "[]") or "[]")
    except:
        pass
    _tag_str = st.text_input(
        "Tags",
        key="hist_tags_input",
        value=", ".join(_existing),
        placeholder="meeting, interview, urgent",
        label_visibility="collapsed",
    )
    _bc1, _bc2 = st.columns([1, 1])
    with _bc1:
        if st.button("💾 Save Tags", key="hist_save_tags", use_container_width=True):
            _new_tags = [t.strip() for t in _tag_str.split(",") if t.strip()]
            try:
                _update_tags(rid, _new_tags)
                st.success("Saved!")
            except Exception as _te:
                st.caption(f"Error: {_te}")
    with _bc2:
        if st.button("✕  Close", key="hist_close", use_container_width=True):
            st.session_state["history_view_id"] = None
            st.session_state["active_dialog"] = None
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# UNIFIED DIALOG DISPATCHER
# ══════════════════════════════════════════════════════════════════════════════
_active = st.session_state.get("active_dialog")

if _active == "result" and st.session_state.get("summary"):

    @st.dialog("Summary Report", width="large")
    def _dlg_result():
        _render_result()

    _dlg_result()

elif _active == "settings":

    @st.dialog("⚙️  Settings", width="large")
    def _dlg_settings():
        _render_settings()

    _dlg_settings()

elif _active == "history" and st.session_state.get("history_view_id"):

    @st.dialog("History Record", width="large")
    def _dlg_history():
        _render_history_detail()

    _dlg_history()


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def render_view_result_btn(label="Open Report", btn_key=""):
    import hashlib

    key = btn_key or ("open_modal_" + hashlib.md5(label.encode()).hexdigest()[:8])
    st.markdown('<div class="result-btn">', unsafe_allow_html=True)
    if st.button(label, key=key, use_container_width=True):
        st.session_state["active_dialog"] = "result"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _open_settings_then_run(audio_path: str, source_label: str):
    """บันทึก pending pipeline แล้วเปิด Settings ให้กรอก key ก่อน"""
    st.session_state["pending_pipeline"] = {
        "path": audio_path,
        "label": source_label,
    }
    st.session_state["active_dialog"] = "settings"
    st.rerun()


def run_pipeline(audio_path: str, source_label: str):
    """ถอดความ + สรุป"""
    import time as _time

    cur_key = st.session_state.get("sb_llm_key", "")
    if not cur_key:
        _open_settings_then_run(audio_path, source_label)
        return

    _t_start = _time.time()
    progress_bar = st.progress(0, text="Initializing...")
    transcript_area = st.empty()
    full_transcript = ""

    try:
        for chunk, pct, status in transcribe_audio(
            audio_path=audio_path,
            engine=stt_engine,
            groq_api_key=groq_key,
            groq_model=groq_model,
            model_size=whisper_model,
            beam_size=beam_size,
            vad_filter=vad_filter,
            chunk_minutes=chunk_minutes,
        ):
            full_transcript += chunk
            progress_bar.progress(min(float(pct), 1.0), text=status)
            display = (
                full_transcript[-3000:]
                if len(full_transcript) > 3000
                else full_transcript
            )
            # colorize [HH:MM:SS] timestamps
            import re as _re

            html_lines = []
            for line in display.split("\n"):
                m = _re.match(r"^(\[\d{2}:\d{2}(?::\d{2})?\])(.*)", line)
                if m:
                    ts, txt = m.group(1), m.group(2)
                    html_lines.append(
                        f'<span class="ts-stamp">{ts}</span><span class="ts-text">{txt}</span>'
                    )
                else:
                    html_lines.append(line)
            html_display = "\n".join(html_lines)
            transcript_area.markdown(
                f'<div class="transcript-box" id="tr-live">{html_display}</div>'
                '<script>var b=document.getElementById("tr-live");if(b)b.scrollTop=b.scrollHeight;</script>',
                unsafe_allow_html=True,
            )

        _t_tr = _time.time() - _t_start
        progress_bar.progress(1.0, text="Transcription complete")
        st.success(
            f"Transcription complete — {len(full_transcript):,} chars  ·  {_t_tr:.0f}s"
        )

    except Exception as e:
        st.error(f"Transcription failed: {e}")
        full_transcript = ""
    finally:
        try:
            os.unlink(audio_path)
        except:
            pass

    if full_transcript:
        st.markdown('<p class="section-label">Summarizing</p>', unsafe_allow_html=True)
        with st.spinner(f"Analyzing with {llm_model}..."):
            try:
                summary = summarize_transcript(
                    transcript=full_transcript,
                    api_key=api_key,
                    mode=summary_mode,
                    model_name=llm_model,
                    provider=selected_provider,
                )

                # คำนวณ quality score จาก heuristics
                _words = len(full_transcript.split())
                _sum_words = len(summary.split())
                _has_ts = "[" in full_transcript and "]" in full_transcript
                _coverage = min(_sum_words / max(_words * 0.08, 1), 1.0)
                _score = int(
                    min((_coverage * 0.5 + (0.3 if _has_ts else 0) + 0.2) * 5, 5)
                )
                st.session_state["quality_score"] = _score
                st.session_state["transcript"] = full_transcript
                st.session_state["summary"] = summary
                st.session_state["source_name"] = source_label
                st.session_state["active_dialog"] = None

                try:
                    _stype = (
                        "youtube"
                        if any(
                            x in source_label.lower() for x in ["youtube", "yt_audio"]
                        )
                        else "audio"
                    )
                    save_result(
                        source_label,
                        full_transcript,
                        summary,
                        _stype,
                        summary_mode,
                        llm_model,
                    )
                except Exception as _e:
                    st.caption(f"DB save skipped: {_e}")

                _t_total = _time.time() - _t_start
                _tstr = (
                    f"{int(_t_total//60)}m {int(_t_total%60)}s"
                    if _t_total >= 60
                    else f"{_t_total:.0f}s"
                )
                st.session_state["last_process_time"] = _tstr
                st.success(f"Analysis complete — saved to history  ·  {_tstr}")
                render_view_result_btn("Open Report", btn_key="open_modal_pipeline")

            except Exception as e:
                st.error(f"Summarization failed: {e}")
                st.info("Check your OpenRouter API key, quota, and model name.")


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    """
<div class="app-header">

  <!-- Waveform animation -->
  <div class="waveform-wrap">
    <svg class="waveform" viewBox="0 0 120 28" xmlns="http://www.w3.org/2000/svg">
      <rect class="bar b1" x="2"   y="10" width="4" height="8"  rx="2"/>
      <rect class="bar b2" x="10"  y="6"  width="4" height="16" rx="2"/>
      <rect class="bar b3" x="18"  y="2"  width="4" height="24" rx="2"/>
      <rect class="bar b4" x="26"  y="6"  width="4" height="16" rx="2"/>
      <rect class="bar b5" x="34"  y="10" width="4" height="8"  rx="2"/>
      <rect class="bar b6" x="42"  y="4"  width="4" height="20" rx="2"/>
      <rect class="bar b7" x="50"  y="8"  width="4" height="12" rx="2"/>
      <rect class="bar b8" x="58"  y="2"  width="4" height="24" rx="2"/>
      <rect class="bar b9" x="66"  y="6"  width="4" height="16" rx="2"/>
      <rect class="bar b10" x="74" y="10" width="4" height="8"  rx="2"/>
      <rect class="bar b11" x="82" y="4"  width="4" height="20" rx="2"/>
      <rect class="bar b12" x="90" y="8"  width="4" height="12" rx="2"/>
      <rect class="bar b13" x="98" y="6"  width="4" height="16" rx="2"/>
      <rect class="bar b14" x="106" y="10" width="4" height="8" rx="2"/>
      <rect class="bar b15" x="114" y="8"  width="4" height="12" rx="2"/>
    </svg>
  </div>

  <!-- Logo + tagline -->
  <div class="app-header-left">
    <span class="app-logo">Transcript<span> AI</span></span>
    <span class="app-tagline">
      <span class="typing-text"></span><span class="cursor">|</span>
    </span>
  </div>

</div>

<script>
(function(){
  var phrases = [
    "Transcribe any audio or video",
    "Summarize meetings instantly",
    "Supports YouTube & audio files",
    "Powered by Groq + OpenRouter"
  ];
  var pi = 0, ci = 0, deleting = false, pause = 0, el = null;

  function findEl(){
    // ลอง querySelector หลายวิธีเพราะ Streamlit อาจ render ช้า
    el = document.querySelector('.typing-text');
    if(!el){
      // ลอง parent document (iframe)
      try { el = window.parent.document.querySelector('.typing-text'); } catch(e){}
    }
    return !!el;
  }

  function tick(){
    if(!el && !findEl()){ setTimeout(tick, 200); return; }
    if(pause > 0){ pause--; setTimeout(tick, 50); return; }
    var phrase = phrases[pi];
    if(!deleting){
      ci++;
      el.textContent = phrase.slice(0, ci);
      if(ci >= phrase.length){ deleting = true; pause = 45; }
      setTimeout(tick, 70);
    } else {
      ci--;
      el.textContent = phrase.slice(0, ci);
      if(ci <= 0){
        ci = 0; deleting = false;
        pi = (pi + 1) % phrases.length;
        pause = 10;
      }
      setTimeout(tick, 38);
    }
  }

  // รอ DOM พร้อมหลายชั้น
  function start(){
    if(findEl()){ setTimeout(tick, 600); }
    else { setTimeout(start, 300); }
  }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', function(){ setTimeout(start, 400); });
  } else {
    setTimeout(start, 400);
  }
})();
</script>
""",
    unsafe_allow_html=True,
)

b1, b2, _sp = st.columns([1, 1, 6], gap="small")
with b1:
    if st.button("⚙️ Settings", key="btn_settings", use_container_width=True):
        st.session_state["pending_pipeline"] = None
        st.session_state["active_dialog"] = "settings"
        st.rerun()
with b2:
    if st.session_state.get("summary"):
        if st.button("📋 Report", key="btn_report", use_container_width=True):
            st.session_state["active_dialog"] = "result"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab_audio, tab_yt, tab_text, tab_history = st.tabs(
    [
        "🎤  Audio",
        "▶️  YouTube",
        "📝  Text",
        "🗂  History",
    ]
)


# ── TAB 1: AUDIO ──────────────────────────────────────────────────────────────
with tab_audio:
    col_l, col_r = st.columns([1, 1], gap="large")
    with col_l:
        st.markdown('<p class="section-label">Upload Audio</p>', unsafe_allow_html=True)
        audio_file = st.file_uploader("Supports .mp3 and .wav", type=["mp3", "wav"])
        if audio_file:
            st.audio(audio_file)
            st.caption(f"{audio_file.name}  ·  {audio_file.size/1_048_576:.1f} MB")
            start_btn = st.button(
                "▶  Transcribe & Summarize",
                use_container_width=True,
                type="primary",
                key="start_audio",
            )
        else:
            start_btn = False
            st.markdown(
                """
<div class="app-card">
  <p class="app-card-label">Instructions</p>
  <p style="font-size:.85rem;line-height:1.7;margin:0">
    Upload a <strong>.mp3</strong> or <strong>.wav</strong> file.<br>
    Settings will open automatically if API keys are not configured.
    <br><br>Requires FFmpeg installed on your system.
  </p>
</div>""",
                unsafe_allow_html=True,
            )

    with col_r:
        st.markdown('<p class="section-label">Output</p>', unsafe_allow_html=True)

        # ── หลัง settings save → run pending pipeline ──────────────
        if st.session_state.get("run_pipeline_now") and st.session_state.get(
            "pending_pipeline"
        ):
            pending = st.session_state.pop("pending_pipeline")
            st.session_state["run_pipeline_now"] = False
            # sync config ใหม่
            api_key = st.session_state.get("sb_llm_key", api_key)
            llm_model = st.session_state.get("sb_llm_model", llm_model)
            summary_mode = st.session_state.get("sb_summary_mode", summary_mode)
            selected_provider = st.session_state.get("sb_provider", selected_provider)
            groq_key = st.session_state.get("sb_groq_key", groq_key)
            groq_model = st.session_state.get("sb_groq_model", groq_model)
            stt_engine = st.session_state.get("sb_stt_engine", stt_engine)
            run_pipeline(pending["path"], pending["label"])

        elif audio_file and start_btn:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=Path(audio_file.name).suffix
            ) as tmp:
                tmp.write(audio_file.read())
                tmp_path = tmp.name
            run_pipeline(tmp_path, audio_file.name)

        elif st.session_state.get("summary") and not audio_file:
            st.info("Previous result available.")
            render_view_result_btn("Open Previous Report", btn_key="open_modal_prev")


# ── TAB 2: YOUTUBE ────────────────────────────────────────────────────────────
with tab_yt:
    col_l, col_r = st.columns([1, 1], gap="large")
    with col_l:
        st.markdown('<p class="section-label">YouTube URL</p>', unsafe_allow_html=True)
        yt_url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed",
            key="yt_url_input",
        )
        if yt_url:
            st.caption(yt_url)
            yt_btn = st.button(
                "▶  Download & Transcribe",
                use_container_width=True,
                type="primary",
                key="start_yt",
            )
        else:
            yt_btn = False
            st.markdown(
                """
<div class="app-card">
  <p class="app-card-label">How it works</p>
  <p style="font-size:.85rem;line-height:1.7;margin:0">
    Paste any YouTube URL. Audio is downloaded automatically via
    <strong>yt-dlp</strong>, then transcribed and summarized.
    <br><br>Requires: <code>pip install yt-dlp</code>
  </p>
</div>""",
                unsafe_allow_html=True,
            )

    with col_r:
        st.markdown('<p class="section-label">Output</p>', unsafe_allow_html=True)

        # pending pipeline from settings save (YouTube)
        if st.session_state.get("run_pipeline_now") and st.session_state.get(
            "pending_pipeline"
        ):
            pending = st.session_state.pop("pending_pipeline")
            st.session_state["run_pipeline_now"] = False
            api_key = st.session_state.get("sb_llm_key", api_key)
            llm_model = st.session_state.get("sb_llm_model", llm_model)
            summary_mode = st.session_state.get("sb_summary_mode", summary_mode)
            selected_provider = st.session_state.get("sb_provider", selected_provider)
            groq_key = st.session_state.get("sb_groq_key", groq_key)
            groq_model = st.session_state.get("sb_groq_model", groq_model)
            stt_engine = st.session_state.get("sb_stt_engine", stt_engine)
            run_pipeline(pending["path"], pending["label"])

        elif yt_url and yt_btn:
            try:
                import yt_dlp
            except ImportError:
                st.error("yt-dlp not installed")
                st.code("pip install yt-dlp", language="bash")
                st.stop()

            with st.spinner("Downloading audio from YouTube..."):
                try:
                    tmp_dir = tempfile.mkdtemp()
                    ydl_opts = {
                        "format": "bestaudio/best",
                        "outtmpl": os.path.join(tmp_dir, "yt_audio.%(ext)s"),
                        "postprocessors": [
                            {
                                "key": "FFmpegExtractAudio",
                                "preferredcodec": "mp3",
                                "preferredquality": "128",
                            }
                        ],
                        "quiet": True,
                        "no_warnings": True,
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(yt_url, download=True)
                        title = info.get("title", "youtube_audio")
                        mins = info.get("duration", 0) // 60

                    mp3_path = os.path.join(tmp_dir, "yt_audio.mp3")
                    if not os.path.exists(mp3_path):
                        for f in os.listdir(tmp_dir):
                            if f.startswith("yt_audio"):
                                mp3_path = os.path.join(tmp_dir, f)
                                break
                    st.success(f"Downloaded: {title} ({mins} min)")
                except Exception as e:
                    st.error(f"Download failed: {e}")
                    st.stop()

            run_pipeline(mp3_path, title or "youtube_audio")


# ── TAB 3: TEXT ───────────────────────────────────────────────────────────────
with tab_text:
    st.markdown('<p class="section-label">Input Text</p>', unsafe_allow_html=True)
    input_mode = st.radio(
        "Source", ["✏️ Type / Paste", "📎 Upload .txt"], horizontal=True
    )
    raw_text = ""

    if input_mode == "✏️ Type / Paste":
        raw_text = st.text_area(
            "Paste transcript here",
            height=300,
            placeholder="[00:00] Speaker A: Hello...\n[00:30] Speaker B: ...",
        )
    else:
        txt_file = st.file_uploader("Upload .txt", type=["txt"], key="txt_uploader")
        if txt_file:
            raw_text = txt_file.read().decode("utf-8", errors="replace")
            st.text_area(
                "Preview",
                raw_text[:2000] + ("..." if len(raw_text) > 2000 else ""),
                height=200,
                disabled=True,
            )
            st.caption(f"{txt_file.name} — {len(raw_text):,} characters")

    # pending pipeline from settings save (text)
    if st.session_state.get("run_pipeline_now") and st.session_state.get(
        "pending_pipeline"
    ):
        pending = st.session_state.pop("pending_pipeline")
        st.session_state["run_pipeline_now"] = False
        api_key = st.session_state.get("sb_llm_key", api_key)
        llm_model = st.session_state.get("sb_llm_model", llm_model)
        summary_mode = st.session_state.get("sb_summary_mode", summary_mode)
        selected_provider = st.session_state.get("sb_provider", selected_provider)
        # text summarize ใช้ raw_text จาก pending
        _txt = pending.get("text", "")
        if _txt:
            with st.spinner(f"Analyzing with {llm_model}..."):
                try:
                    summary = summarize_transcript(
                        _txt, api_key, summary_mode, llm_model, selected_provider
                    )
                    st.session_state["transcript"] = _txt
                    st.session_state["summary"] = summary
                    st.session_state["source_name"] = "text_input"
                    st.session_state["active_dialog"] = None
                    try:
                        save_result(
                            "text_input", _txt, summary, "text", summary_mode, llm_model
                        )
                    except Exception as _e:
                        st.caption(f"DB: {_e}")
                    st.success("Analysis complete — saved to history")
                    render_view_result_btn("Open Report", btn_key="open_modal_text_p")
                except Exception as e:
                    st.error(f"Failed: {e}")

    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        sum_btn = st.button(
            "▶  Summarize",
            use_container_width=True,
            disabled=not raw_text,
            type="primary",
            key="sum_text",
        )
    with col_info:
        if not raw_text:
            st.info("Paste or upload text first")

    if sum_btn and raw_text:
        cur_key = st.session_state.get("sb_llm_key", "")
        if not cur_key:
            # เปิด settings ก่อน
            st.session_state["pending_pipeline"] = {
                "text": raw_text,
                "path": "",
                "label": "text_input",
            }
            st.session_state["active_dialog"] = "settings"
            st.rerun()
        else:
            with st.spinner(f"Analyzing with {llm_model}..."):
                try:
                    summary = summarize_transcript(
                        raw_text, api_key, summary_mode, llm_model, selected_provider
                    )
                    st.session_state["transcript"] = raw_text
                    st.session_state["summary"] = summary
                    st.session_state["source_name"] = "text_input"
                    st.session_state["active_dialog"] = None
                    try:
                        save_result(
                            "text_input",
                            raw_text,
                            summary,
                            "text",
                            summary_mode,
                            llm_model,
                        )
                    except Exception as _e:
                        st.caption(f"DB: {_e}")
                    st.success("Analysis complete — saved to history")
                    render_view_result_btn("Open Report", btn_key="open_modal_text")
                except Exception as e:
                    st.error(f"Failed: {e}")
                    st.info("Check API key, quota, and model name.")


# ── TAB 4: HISTORY ────────────────────────────────────────────────────────────
with tab_history:
    st.markdown('<p class="section-label">Saved Results</p>', unsafe_allow_html=True)

    stats = get_stats()
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Total Saved", stats["total"])
    sc2.metric("Total Characters", f'{stats["total_chars"]:,}')
    sc3.metric(
        "By Type", ", ".join(f"{v} {k}" for k, v in stats["by_type"].items()) or "—"
    )
    st.markdown("---")

    q = st.text_input(
        "Search",
        placeholder="Search filename or content...",
        key="history_search",
        label_visibility="collapsed",
    )

    records = search(q, 100) if q else get_all(100)

    if not records:
        st.info("No history yet — start transcribing to see results here.")
    else:
        st.caption(f"{len(records)} record(s)")
        for rec in records:
            icon = {"audio": "🎙️", "youtube": "▶️", "text": "📝"}.get(
                rec["source_type"], "📄"
            )
            name = rec["source_name"]
            date = rec["created_at"]
            chars = rec["char_count"]
            model = rec.get("llm_model", "")
            preview = (rec["summary"] or "")[:180]
            if len(rec["summary"] or "") > 180:
                preview += "..."

            with st.container():
                ci, cb = st.columns([5, 1], gap="small")
                with ci:
                    import json as _json2

                    _tr = []
                    try:
                        _tr = _json2.loads(rec.get("tags", "[]") or "[]")
                    except:
                        pass
                    _th = " ".join(f'<span class="tag-chip">#{t}</span>' for t in _tr)
                    _extra = f"<br>{_th}" if _tr else ""
                    st.markdown(
                        f"**{icon} {name}**  "
                        f"<span style='font-size:.78rem;color:var(--text-muted,#8a6040)'>"
                        f"{date} &nbsp;·&nbsp; {chars:,} chars &nbsp;·&nbsp; {model}</span>"
                        + _extra,
                        unsafe_allow_html=True,
                    )
                    st.caption(preview)
                with cb:
                    if st.button(
                        "View", key=f"hv_{rec['id']}", use_container_width=True
                    ):
                        st.session_state["history_view_id"] = rec["id"]
                        st.session_state["active_dialog"] = "history"
                        st.rerun()
                    if st.button("🗑", key=f"hd_{rec['id']}", use_container_width=True):
                        delete_by_id(rec["id"])
                        st.session_state["active_dialog"] = None
                        st.session_state["history_view_id"] = None
                        st.rerun()
                st.markdown(
                    "<hr style='margin:.3rem 0;border-color:rgba(180,100,20,.1)'>",
                    unsafe_allow_html=True,
                )
