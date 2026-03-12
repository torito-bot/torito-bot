import os
import json
from pathlib import Path
import psycopg

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if DATABASE_URL:
        return psycopg.connect(DATABASE_URL)
    raise ValueError("DATABASE_URL not found")


def load_json_file(filename: str):
    file_path = DATA_DIR / filename
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def make_referral_code(user_id: int) -> str:
    return f"u{user_id}"


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        user_id BIGINT UNIQUE,
        username TEXT,
        full_name TEXT,
        referral_code TEXT UNIQUE,
        referred_by BIGINT,
        first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        event TEXT,
        event_value TEXT,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        ads INTEGER NOT NULL,
        days INTEGER NOT NULL,
        price REAL NOT NULL,
        cost REAL NOT NULL,
        product_type TEXT NOT NULL
    )
    """)

    cursor.execute("""
    ALTER TABLE users
    ADD COLUMN IF NOT EXISTS referral_code TEXT
    """)

    cursor.execute("""
    ALTER TABLE users
    ADD COLUMN IF NOT EXISTS referred_by BIGINT
    """)

    conn.commit()
    conn.close()


def seed_products():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]

    if count == 0:
        top_products = load_json_file("top_products.json")
        trending_products = load_json_file("trending_products.json")

        for p in top_products:
            cursor.execute("""
            INSERT INTO products (name, ads, days, price, cost, product_type)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (p["name"], p["ads"], p["days"], p["price"], p["cost"], "top"))

        for p in trending_products:
            cursor.execute("""
            INSERT INTO products (name, ads, days, price, cost, product_type)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (p["name"], p["ads"], p["days"], p["price"], p["cost"], "trending"))

    conn.commit()
    conn.close()


def get_products_by_type(product_type):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT name, ads, days, price, cost
    FROM products
    WHERE product_type = %s
    ORDER BY ads DESC
    """, (product_type,))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "name": row[0],
            "ads": row[1],
            "days": row[2],
            "price": row[3],
            "cost": row[4],
        }
        for row in rows
    ]


def add_user(user_id, username=None, full_name=None):
    conn = get_connection()
    cursor = conn.cursor()

    referral_code = make_referral_code(user_id)

    cursor.execute("""
    INSERT INTO users (user_id, username, full_name, referral_code)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (user_id) DO UPDATE
    SET username = EXCLUDED.username,
        full_name = EXCLUDED.full_name
    """, (user_id, username, full_name, referral_code))

    conn.commit()
    conn.close()


def set_referral(user_id, referral_code):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT user_id FROM users
    WHERE referral_code = %s
    """, (referral_code,))
    inviter = cursor.fetchone()

    if not inviter:
        conn.close()
        return {"status": "invalid"}

    inviter_id = inviter[0]

    if inviter_id == user_id:
        conn.close()
        return {"status": "self"}

    cursor.execute("""
    SELECT referred_by FROM users
    WHERE user_id = %s
    """, (user_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return {"status": "user_not_found"}

    if row[0] is not None:
        conn.close()
        return {"status": "already_set"}

    cursor.execute("""
    UPDATE users
    SET referred_by = %s
    WHERE user_id = %s
    """, (inviter_id, user_id))

    conn.commit()
    conn.close()

    return {"status": "ok", "inviter_id": inviter_id}


def get_user_referral_info(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT referral_code
    FROM users
    WHERE user_id = %s
    """, (user_id,))
    row = cursor.fetchone()

    if row and row[0]:
        referral_code = row[0]
    else:
        referral_code = make_referral_code(user_id)

        cursor.execute("""
        UPDATE users
        SET referral_code = %s
        WHERE user_id = %s
        """, (referral_code, user_id))

        conn.commit()

    cursor.execute("""
    SELECT COUNT(*)
    FROM users
    WHERE referred_by = %s
    """, (user_id,))
    referrals_count = cursor.fetchone()[0]

    conn.close()

    return {
        "referral_code": referral_code,
        "referrals_count": referrals_count
    }


def log_event(user_id, event, event_value=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO events (user_id, event, event_value)
    VALUES (%s, %s, %s)
    """, (user_id, event, event_value))

    conn.commit()
    conn.close()


def get_total_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]

    conn.close()
    return total


def get_total_referrals():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM users
    WHERE referred_by IS NOT NULL
    """)
    total = cursor.fetchone()[0]

    conn.close()
    return total


def count_events(event, event_value=None):
    conn = get_connection()
    cursor = conn.cursor()

    if event_value is None:
        cursor.execute(
            "SELECT COUNT(*) FROM events WHERE event = %s",
            (event,)
        )
    else:
        cursor.execute(
            "SELECT COUNT(*) FROM events WHERE event = %s AND event_value = %s",
            (event, event_value)
        )

    total = cursor.fetchone()[0]
    conn.close()
    return total


def get_top_clicked_products(limit=5):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT event_value, COUNT(*) as total
    FROM events
    WHERE event = 'click_action'
    GROUP BY event_value
    ORDER BY total DESC
    LIMIT %s
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_top_referrers(limit=5):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        COALESCE(NULLIF(full_name, ''), username, CAST(user_id AS TEXT)) as referrer,
        COUNT(*) as total
    FROM users
    WHERE referred_by IS NOT NULL
    GROUP BY referred_by, full_name, username, user_id
    ORDER BY total DESC
    LIMIT %s
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return rows
