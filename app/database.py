"""
database.py
Lightweight SQLite storage for verified product records.
Stores BOTH the initial user-provided data and the AI-extracted/enriched
data, only after the user has clicked "Verify & Save".
"""

import sqlite3
import json
import os
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "product_intelligence.db")


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            initial_data TEXT,       -- JSON: what the user originally typed in
            attributes TEXT,         -- JSON: final approved attributes (extracted + confirmed)
            confidence_scores TEXT,  -- JSON
            source_reference TEXT,   -- JSON
            validation_status TEXT,
            verified_by_user INTEGER DEFAULT 1,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def insert_product(record: dict):
    """
    record expects keys: name, category, initial_data (dict), attributes (dict),
    confidence_scores (dict), source_reference (dict), validation_status (str)
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO products
            (name, category, initial_data, attributes, confidence_scores,
             source_reference, validation_status, verified_by_user, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record.get("name", ""),
        record.get("category", ""),
        json.dumps(record.get("initial_data", {})),
        json.dumps(record.get("attributes", {})),
        json.dumps(record.get("confidence_scores", {})),
        json.dumps(record.get("source_reference", {})),
        record.get("validation_status", ""),
        1,
        datetime.datetime.now().isoformat(timespec="seconds"),
    ))
    conn.commit()
    product_id = c.lastrowid
    conn.close()
    return product_id


def get_all_products(search: str = ""):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if search:
        c.execute(
            "SELECT * FROM products WHERE name LIKE ? OR category LIKE ? ORDER BY id DESC",
            (f"%{search}%", f"%{search}%"),
        )
    else:
        c.execute("SELECT * FROM products ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    results = []
    for row in rows:
        item = dict(row)
        for field in ("initial_data", "attributes", "confidence_scores", "source_reference"):
            try:
                item[field] = json.loads(item[field]) if item[field] else {}
            except json.JSONDecodeError:
                item[field] = {}
        results.append(item)
    return results


def delete_product(product_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()


def get_product_count():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM products")
    count = c.fetchone()[0]
    conn.close()
    return count
