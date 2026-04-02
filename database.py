import sqlite3
import json
from datetime import datetime, date

DB_FILE = "sinzhu.db"

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        onex INTEGER DEFAULT 500,
        daily_claim TEXT DEFAULT NULL,
        welkin_claim TEXT DEFAULT NULL,
        hclaim_date TEXT DEFAULT NULL,
        total_waifus INTEGER DEFAULT 0,
        favorite_waifu_id INTEGER DEFAULT NULL,
        chat_mode INTEGER DEFAULT 0
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS waifus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        anime TEXT,
        rarity TEXT,
        image_url TEXT,
        added_by INTEGER DEFAULT NULL
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS user_waifus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        waifu_id INTEGER,
        obtained_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id),
        FOREIGN KEY(waifu_id) REFERENCES waifus(id)
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS group_data (
        chat_id INTEGER PRIMARY KEY,
        message_count INTEGER DEFAULT 0,
        spawn_interval INTEGER DEFAULT 15,
        current_waifu_id INTEGER DEFAULT NULL,
        current_waifu_claimed INTEGER DEFAULT 0,
        active_chat_mode INTEGER DEFAULT 0
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user INTEGER,
        to_user INTEGER,
        amount INTEGER,
        type TEXT,
        created_at TEXT
    )""")
    
    conn.commit()
    conn.close()

def get_user(user_id, username=None, first_name=None):
    conn = get_conn()
    c = conn.cursor()
    user = c.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    if not user:
        c.execute("INSERT INTO users (user_id, username, first_name) VALUES (?,?,?)",
                  (user_id, username or "", first_name or ""))
        conn.commit()
        user = c.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return dict(user)

def update_user(user_id, **kwargs):
    conn = get_conn()
    c = conn.cursor()
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [user_id]
    c.execute(f"UPDATE users SET {sets} WHERE user_id=?", vals)
    conn.commit()
    conn.close()

def get_all_waifus():
    conn = get_conn()
    waifus = conn.execute("SELECT * FROM waifus").fetchall()
    conn.close()
    return [dict(w) for w in waifus]

def add_waifu_to_db(name, anime, rarity, image_url, added_by=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO waifus (name, anime, rarity, image_url, added_by) VALUES (?,?,?,?,?)",
              (name, anime, rarity, image_url, added_by))
    wid = c.lastrowid
    conn.commit()
    conn.close()
    return wid

def delete_waifu_from_db(waifu_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM waifus WHERE id=?", (waifu_id,))
    c.execute("DELETE FROM user_waifus WHERE waifu_id=?", (waifu_id,))
    conn.commit()
    conn.close()

def give_waifu_to_user(user_id, waifu_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO user_waifus (user_id, waifu_id, obtained_at) VALUES (?,?,?)",
              (user_id, waifu_id, datetime.now().isoformat()))
    c.execute("UPDATE users SET total_waifus = total_waifus + 1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def get_user_waifus(user_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT uw.id, w.name, w.anime, w.rarity, w.image_url, uw.obtained_at
        FROM user_waifus uw JOIN waifus w ON uw.waifu_id = w.id
        WHERE uw.user_id = ?
        ORDER BY uw.obtained_at DESC
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def remove_user_waifu(uw_id, user_id):
    conn = get_conn()
    c = conn.cursor()
    waifu = c.execute("SELECT * FROM user_waifus WHERE id=? AND user_id=?", (uw_id, user_id)).fetchone()
    if waifu:
        c.execute("DELETE FROM user_waifus WHERE id=?", (uw_id,))
        c.execute("UPDATE users SET total_waifus = MAX(0, total_waifus - 1) WHERE user_id=?", (user_id,))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def get_waifu_by_uw_id(uw_id):
    conn = get_conn()
    row = conn.execute("""
        SELECT uw.id, uw.user_id, w.name, w.anime, w.rarity, w.image_url, w.id as waifu_id
        FROM user_waifus uw JOIN waifus w ON uw.waifu_id = w.id
        WHERE uw.id=?
    """, (uw_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_group(chat_id):
    conn = get_conn()
    c = conn.cursor()
    row = c.execute("SELECT * FROM group_data WHERE chat_id=?", (chat_id,)).fetchone()
    if not row:
        c.execute("INSERT INTO group_data (chat_id) VALUES (?)", (chat_id,))
        conn.commit()
        row = c.execute("SELECT * FROM group_data WHERE chat_id=?", (chat_id,)).fetchone()
    conn.close()
    return dict(row)

def update_group(chat_id, **kwargs):
    conn = get_conn()
    c = conn.cursor()
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [chat_id]
    c.execute(f"UPDATE group_data SET {sets} WHERE chat_id=?", vals)
    conn.commit()
    conn.close()

def get_top_collectors(limit=10):
    conn = get_conn()
    rows = conn.execute("""
        SELECT user_id, username, first_name, total_waifus
        FROM users ORDER BY total_waifus DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_top_rich(limit=10):
    conn = get_conn()
    rows = conn.execute("""
        SELECT user_id, username, first_name, onex
        FROM users ORDER BY onex DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_top_groups(limit=10):
    conn = get_conn()
    rows = conn.execute("""
        SELECT chat_id, message_count FROM group_data
        ORDER BY message_count DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def seed_waifus():
    from waifu_data import DEFAULT_WAIFUS
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM waifus").fetchone()[0]
    conn.close()
    if count == 0:
        for w in DEFAULT_WAIFUS:
            add_waifu_to_db(w["name"], w["anime"], w["rarity"], w["image"])
  
