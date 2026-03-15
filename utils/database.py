"""
utils/database.py — SQLite history store
"""

import sqlite3, json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "history.db"


def _conn():
    c = sqlite3.connect(str(DB_PATH))
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with _conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at   TEXT NOT NULL,
                source_name  TEXT NOT NULL,
                source_type  TEXT NOT NULL DEFAULT 'audio',
                char_count   INTEGER,
                summary_mode TEXT,
                llm_model    TEXT,
                transcript   TEXT,
                summary      TEXT
            )
        """
        )
        c.commit()


def save_result(
    source_name, transcript, summary, source_type="audio", summary_mode="", llm_model=""
) -> int:
    init_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _conn() as c:
        cur = c.execute(
            """
            INSERT INTO history
              (created_at,source_name,source_type,char_count,summary_mode,llm_model,transcript,summary)
            VALUES (?,?,?,?,?,?,?,?)
        """,
            (
                now,
                source_name,
                source_type,
                len(transcript),
                summary_mode,
                llm_model,
                transcript,
                summary,
            ),
        )
        c.commit()
        return cur.lastrowid


def get_all(limit=200):
    init_db()
    with _conn() as c:
        rows = c.execute(
            """
            SELECT id,created_at,source_name,source_type,
                   char_count,summary_mode,llm_model,summary
            FROM history ORDER BY id DESC LIMIT ?
        """,
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_by_id(rid):
    init_db()
    with _conn() as c:
        row = c.execute("SELECT * FROM history WHERE id=?", (rid,)).fetchone()
    return dict(row) if row else None


def delete_by_id(rid):
    init_db()
    with _conn() as c:
        c.execute("DELETE FROM history WHERE id=?", (rid,))
        c.commit()


def search(query, limit=50):
    init_db()
    q = f"%{query}%"
    with _conn() as c:
        rows = c.execute(
            """
            SELECT id,created_at,source_name,source_type,
                   char_count,summary_mode,llm_model,summary
            FROM history
            WHERE source_name LIKE ? OR summary LIKE ?
            ORDER BY id DESC LIMIT ?
        """,
            (q, q, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def get_stats():
    init_db()
    with _conn() as c:
        total = c.execute("SELECT COUNT(*) FROM history").fetchone()[0]
        total_chars = c.execute(
            "SELECT COALESCE(SUM(char_count),0) FROM history"
        ).fetchone()[0]
        by_type = c.execute(
            "SELECT source_type,COUNT(*) FROM history GROUP BY source_type"
        ).fetchall()
    return {
        "total": total,
        "total_chars": total_chars,
        "by_type": {r[0]: r[1] for r in by_type},
    }
