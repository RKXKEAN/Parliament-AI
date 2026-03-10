"""
Thai Parliament AI — Transcription & Summarization System
"""

import streamlit as st
import tempfile
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Parliament AI — Transcription & Summarization",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.transcriber import transcribe_audio, WHISPER_MODELS, STT_ENGINES, GROQ_MODELS
from utils.summarizer import summarize_transcript, SUMMARY_MODES, PROVIDERS
from utils.exporter import export_txt, export_docx


# ══════════════════════════════════════════════════════════════════════════════
# LOAD STYLESHEET
# ══════════════════════════════════════════════════════════════════════════════
def _load_css(path: str = "style.css") -> None:
    """โหลดไฟล์ style.css แล้ว inject เข้า Streamlit"""
    css_file = Path(__file__).parent / path
    if css_file.exists():
        css = css_file.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ ไม่พบไฟล์ {path} — หน้าตาอาจผิดปกติ")


_load_css()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="parl-header">
  <div class="parl-crown">🏛️</div>
  <h1 class="parl-title">Parliament AI</h1>
  <p class="parl-subtitle">Thai Legislative Transcription &amp; Summarization System</p>
  <div class="parl-divider"></div>
</div>
""",
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ══════════════════════════════════════════════════════════════════════════════
if "show_result_modal" not in st.session_state:
    st.session_state["show_result_modal"] = False
if "transcript" not in st.session_state:
    st.session_state["transcript"] = ""
if "summary" not in st.session_state:
    st.session_state["summary"] = ""
if "source_name" not in st.session_state:
    st.session_state["source_name"] = "output"


# ══════════════════════════════════════════════════════════════════════════════
# RESULT MODAL
# ══════════════════════════════════════════════════════════════════════════════
def show_result_modal():
    """Render the full-screen result modal using st.dialog."""
    transcript = st.session_state.get("transcript", "")
    summary = st.session_state.get("summary", "")
    source_name = st.session_state.get("source_name", "output")
    stem = Path(source_name).stem

    st.markdown(
        f"""
    <div style="display:flex;align-items:center;gap:.8rem;margin-bottom:1rem;">
      <span style="font-family:'Cinzel',serif;font-size:1.1rem;color:#e8cc7a;">📋 Meeting Report</span>
      <span style="font-size:.75rem;color:#7a8499;font-style:italic;">{source_name}</span>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ── Summary ─────────────────────────────────────────────────
    st.markdown('<p class="section-label">📋 Summary</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Transcript toggle ────────────────────────────────────────
    with st.expander("🎙️ View Full Transcript", expanded=False):
        st.caption(f"{len(transcript):,} characters")
        st.text_area(
            "",
            transcript,
            height=380,
            label_visibility="collapsed",
            key="modal_transcript_view",
        )

    # ── Downloads ────────────────────────────────────────────────
    st.markdown(
        '<p class="section-label" style="margin-top:1.2rem">⬇ Download Report</p>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            "📄 Summary (.txt)",
            data=export_txt(transcript, summary),
            file_name=f"{stem}_summary.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_txt_modal",
        )
    with c2:
        try:
            st.download_button(
                "📝 Report (.docx)",
                data=export_docx(transcript, summary),
                file_name=f"{stem}_report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                key="dl_docx_modal",
            )
        except Exception as e:
            st.caption(f"⚠️ DOCX unavailable: {e}")
    with c3:
        st.download_button(
            "📜 Transcript (.txt)",
            data=transcript.encode("utf-8"),
            file_name=f"{stem}_transcript.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_tr_modal",
        )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✕  Close", key="close_modal", use_container_width=False):
        st.session_state["show_result_modal"] = False
        st.rerun()


# Trigger modal via st.dialog
if st.session_state["show_result_modal"] and st.session_state.get("summary"):

    @st.dialog("📋 Parliament AI — Meeting Report", width="large")
    def _modal():
        show_result_modal()

    _modal()


# ══════════════════════════════════════════════════════════════════════════════
# VIEW RESULT BUTTON (shown after pipeline completes)
# ══════════════════════════════════════════════════════════════════════════════
def render_view_result_btn(label: str = "📋  View Full Report"):
    """Gold outline button that opens the result modal."""
    st.markdown('<div class="result-btn">', unsafe_allow_html=True)
    if st.button(label, key=f"open_modal_{label[:6]}", use_container_width=True):
        st.session_state["show_result_modal"] = True
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
def run_pipeline(audio_path: str, source_label: str):
    progress_bar = st.progress(0, text="Initializing…")
    transcript_area = st.empty()
    full_transcript = ""

    try:
        for chunk_text, pct, status in transcribe_audio(
            audio_path=audio_path,
            engine=stt_engine,
            groq_api_key=groq_key,
            groq_model=groq_model,
            model_size=whisper_model,
            beam_size=beam_size,
            vad_filter=vad_filter,
            chunk_minutes=chunk_minutes,
        ):
            full_transcript += chunk_text
            progress_bar.progress(min(float(pct), 1.0), text=status)
            display = (
                full_transcript[-3000:]
                if len(full_transcript) > 3000
                else full_transcript
            )
            transcript_area.markdown(
                f'<div class="transcript-box">{display}</div>', unsafe_allow_html=True
            )

        progress_bar.progress(1.0, text="✅ Transcription complete")
        st.success(f"✅ Transcription complete — {len(full_transcript):,} characters")

    except Exception as e:
        st.error(f"❌ Transcription failed: {e}")
        full_transcript = ""
    finally:
        try:
            os.unlink(audio_path)
        except:
            pass

    if full_transcript:
        st.markdown(
            f'<p class="section-label">🤖 Summarizing with {llm_model}</p>',
            unsafe_allow_html=True,
        )
        with st.spinner("Analyzing legislative content…"):
            try:
                summary = summarize_transcript(
                    transcript=full_transcript,
                    api_key=gemini_key,
                    mode=summary_mode,
                    model_name=llm_model,
                    provider=selected_provider,
                )

                st.session_state["transcript"] = full_transcript
                st.session_state["summary"] = summary
                st.session_state["source_name"] = source_label
                st.session_state["show_result_modal"] = False

                st.success("✅ Analysis complete")
                render_view_result_btn("📋  Open Full Report")

            except Exception as e:
                st.error(f"❌ Summarization failed: {e}")
                st.info("💡 Check your API key, quota, and model name.")


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        '<p class="sidebar-section-title">⚙ Configuration</p>', unsafe_allow_html=True
    )

    # ── Speech-to-Text ──────────────────────────────────────────
    st.markdown(
        '<p class="sidebar-section-title">🎙 Speech-to-Text</p>', unsafe_allow_html=True
    )
    stt_engine = st.selectbox(
        "Engine",
        key="sb_stt_engine",
        options=list(STT_ENGINES.keys()),
        format_func=lambda k: STT_ENGINES[k]["label"],
        index=0,
    )
    st.caption(STT_ENGINES[stt_engine]["desc"])

    if stt_engine == "groq":
        groq_key = st.text_input(
            "Groq API Key",
            key="sb_groq_key",
            type="password",
            value=os.getenv("GROQ_API_KEY", ""),
            placeholder="gsk_...",
            help="Free at console.groq.com",
        )
        if groq_key:
            st.success("⚡ Groq connected")
        else:
            st.warning("Add key or set GROQ_API_KEY in .env")

        groq_model = st.selectbox(
            "Groq Model",
            key="sb_groq_model",
            options=list(GROQ_MODELS.keys()),
            format_func=lambda k: GROQ_MODELS[k]["label"],
        )
        whisper_model = "small"
    else:
        groq_key = ""
        groq_model = "whisper-large-v3-turbo"
        whisper_model = st.selectbox(
            "Whisper Model",
            key="sb_whisper_model",
            options=list(WHISPER_MODELS.keys()),
            index=2,
            format_func=lambda k: WHISPER_MODELS[k]["label"],
        )
        st.caption(WHISPER_MODELS[whisper_model]["desc"])

    # ── LLM Provider ────────────────────────────────────────────
    st.markdown(
        '<p class="sidebar-section-title">🤖 LLM Provider</p>', unsafe_allow_html=True
    )
    from utils.summarizer import PROVIDERS

    selected_provider = st.selectbox(
        "Provider",
        key="sb_provider",
        options=list(PROVIDERS.keys()),
        format_func=lambda k: PROVIDERS[k]["label"],
        index=1,
    )
    st.caption(PROVIDERS[selected_provider]["desc"])

    env_key_map = {
        "gemini": os.getenv("GEMINI_API_KEY", ""),
        "openrouter": os.getenv("OPENROUTER_API_KEY", ""),
        "groq_llm": os.getenv("GROQ_API_KEY", ""),
    }
    gemini_key = st.text_input(
        "LLM API Key",
        key="sb_llm_key",
        type="password",
        value=env_key_map.get(selected_provider, ""),
        placeholder=PROVIDERS[selected_provider]["placeholder"],
    )
    if gemini_key:
        st.success("🔑 LLM API Key ready")
    else:
        st.warning("Add key or set in .env")

    llm_model = st.selectbox(
        "Model",
        key="sb_llm_model",
        options=PROVIDERS[selected_provider]["models"],
    )

    # ── Summary Style ────────────────────────────────────────────
    st.markdown(
        '<p class="sidebar-section-title">📋 Summary Style</p>', unsafe_allow_html=True
    )
    summary_mode = st.selectbox(
        "Format",
        key="sb_summary_mode",
        options=list(SUMMARY_MODES.keys()),
        format_func=lambda k: SUMMARY_MODES[k]["label"],
    )
    st.caption(SUMMARY_MODES[summary_mode]["desc"])

    # ── Advanced ─────────────────────────────────────────────────
    st.markdown(
        '<p class="sidebar-section-title">🔧 Advanced</p>', unsafe_allow_html=True
    )
    beam_size = st.slider("Beam Size", 1, 5, 2, key="sb_beam")
    vad_filter = st.checkbox("VAD Filter", value=True, key="sb_vad")
    chunk_minutes = st.slider("Chunk Size (min)", 1, 10, 5, key="sb_chunk")

    # ── Last Report ──────────────────────────────────────────────
    if st.session_state.get("summary"):
        st.markdown("---")
        if st.button(
            "📋 View Last Report", use_container_width=True, key="sidebar_modal_btn"
        ):
            st.session_state["show_result_modal"] = True
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab_audio, tab_yt, tab_text = st.tabs(
    [
        "🎤  Audio Upload",
        "▶️  YouTube Link",
        "📝  Paste Text",
    ]
)


# ── TAB 1: AUDIO ──────────────────────────────────────────────────────────────
with tab_audio:
    col_l, col_r = st.columns([1, 1], gap="large")
    with col_l:
        st.markdown(
            '<p class="section-label">📂 Upload Audio File</p>', unsafe_allow_html=True
        )
        audio_file = st.file_uploader("Supports .mp3 and .wav", type=["mp3", "wav"])
        if audio_file:
            st.audio(audio_file)
            st.caption(f"📁 {audio_file.name}  ·  {audio_file.size/1_048_576:.1f} MB")
            start_btn = st.button(
                "▶ Transcribe & Summarize",
                use_container_width=True,
                disabled=not gemini_key,
                type="primary",
                key="start_audio",
            )
        else:
            start_btn = False
            st.markdown(
                """
<div class="parl-card">
  <p class="parl-card-title">Instructions</p>
  <p style="color:#7a8499;font-size:.85rem;line-height:1.7;margin:0">
    Upload a <strong style="color:#c9a84c">.mp3</strong> or
    <strong style="color:#c9a84c">.wav</strong> recording of a Thai parliamentary session.
    The system transcribes speech and generates an official structured meeting report.
    <br><br>Requires FFmpeg installed on your system.
  </p>
</div>""",
                unsafe_allow_html=True,
            )

    with col_r:
        st.markdown(
            '<p class="section-label">📊 Progress & Output</p>', unsafe_allow_html=True
        )
        if audio_file and start_btn:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=Path(audio_file.name).suffix
            ) as tmp:
                tmp.write(audio_file.read())
                tmp_path = tmp.name
            run_pipeline(tmp_path, audio_file.name)
        elif st.session_state.get("summary") and not audio_file:
            st.info("Previous session available.")
            render_view_result_btn("📋  Open Previous Report")


# ── TAB 2: YOUTUBE ────────────────────────────────────────────────────────────
with tab_yt:
    col_l, col_r = st.columns([1, 1], gap="large")
    with col_l:
        st.markdown(
            '<p class="section-label">▶ YouTube URL</p>', unsafe_allow_html=True
        )
        yt_url = st.text_input(
            "Paste YouTube link",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed",
        )
        if yt_url:
            st.markdown(
                f"""<div class="parl-card" style="margin-top:.8rem">
  <p class="parl-card-title">URL Detected</p>
  <p style="color:#7a8499;font-size:.82rem;word-break:break-all;margin:0">{yt_url}</p>
</div>""",
                unsafe_allow_html=True,
            )
            yt_btn = st.button(
                "▶ Download & Transcribe",
                use_container_width=True,
                disabled=not gemini_key,
                type="primary",
                key="start_yt",
            )
        else:
            yt_btn = False
            st.markdown(
                """<div class="parl-card">
  <p class="parl-card-title">How it works</p>
  <p style="color:#7a8499;font-size:.85rem;line-height:1.7;margin:0">
    Paste a YouTube URL of any Thai parliament session or political event.
    Audio is downloaded automatically via <strong style="color:#c9a84c">yt-dlp</strong>,
    then transcribed and analyzed.<br><br>
    Requires: <code style="color:#c9a84c">pip install yt-dlp</code>
  </p>
</div>""",
                unsafe_allow_html=True,
            )

    with col_r:
        st.markdown(
            '<p class="section-label">📊 Progress & Output</p>', unsafe_allow_html=True
        )
        if yt_url and yt_btn:
            try:
                import yt_dlp
            except ImportError:
                st.error("❌ yt-dlp not installed")
                st.code("pip install yt-dlp", language="bash")
                st.stop()

            with st.spinner("📥 Downloading audio from YouTube…"):
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

                    st.success(f"✅ Downloaded: **{title}** ({mins} min)")
                except Exception as e:
                    st.error(f"❌ Download failed: {e}")
                    st.info("💡 Check URL or video may be restricted.")
                    st.stop()

            run_pipeline(mp3_path, title or "youtube_audio")


# ── TAB 3: PASTE TEXT ─────────────────────────────────────────────────────────
with tab_text:
    st.markdown('<p class="section-label">📝 Input Text</p>', unsafe_allow_html=True)
    input_mode = st.radio(
        "Source", ["✏️ Type / Paste", "📎 Upload .txt"], horizontal=True
    )
    raw_text = ""

    if input_mode == "✏️ Type / Paste":
        raw_text = st.text_area(
            "Paste meeting transcript here",
            height=300,
            placeholder=(
                "[00:00] ประธานสภา: ขอเปิดการประชุมสภาผู้แทนราษฎร ครั้งที่ ๑\n"
                "[00:20] สมาชิก: ท่านประธานครับ ผมขอตั้งกระทู้ถามสดในเรื่อง...\n"
                "[01:05] รัฐมนตรี: ขอบคุณท่านสมาชิก ผมขอชี้แจงว่า...\n"
            ),
        )
    else:
        txt_file = st.file_uploader("Upload .txt", type=["txt"], key="txt_uploader")
        if txt_file:
            raw_text = txt_file.read().decode("utf-8", errors="replace")
            st.text_area(
                "Preview",
                raw_text[:2000] + ("…" if len(raw_text) > 2000 else ""),
                height=200,
                disabled=True,
            )
            st.caption(f"📄 {txt_file.name} — {len(raw_text):,} characters")

    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        sum_btn = st.button(
            "⚡ Analyze & Summarize",
            use_container_width=True,
            disabled=(not raw_text or not gemini_key),
            type="primary",
            key="sum_text",
        )
    with col_info:
        if not gemini_key:
            st.warning("⚠️ Add LLM API Key in sidebar")
        elif not raw_text:
            st.info("👆 Paste or upload transcript text first")

    if sum_btn and raw_text:
        with st.spinner(f"Analyzing with {llm_model}…"):
            try:
                summary = summarize_transcript(
                    raw_text, gemini_key, summary_mode, llm_model, selected_provider
                )
                st.session_state["transcript"] = raw_text
                st.session_state["summary"] = summary
                st.session_state["source_name"] = "text_input"
                st.session_state["show_result_modal"] = False
                st.success("✅ Analysis complete")
                render_view_result_btn("📋  Open Full Report")
            except Exception as e:
                st.error(f"❌ Failed: {e}")
                st.info("💡 Check API key, quota, and model name.")
