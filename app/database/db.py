import os
import json
from pathlib import Path
import psycopg

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

DATABASE_URL = os.getenv("DATABASE_URL")

BASE_FREE_LIMIT = 5
REFERRAL_BONUS_PER_FRIEND = 2


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
    CREATE TABLE IF NOT EXISTS usage_daily (
        user_id BIGINT,
        usage_date DATE,
        count INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, usage_date)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meta_ads_raw (
        id SERIAL PRIMARY KEY,
        ad_id TEXT UNIQUE,
        geo TEXT NOT NULL,
        page_name TEXT,
        ad_text TEXT,
        landing_url TEXT,
        snapshot_url TEXT,
        start_date TIMESTAMP,
        active_days INTEGER DEFAULT 0,
        raw_payload JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meta_ads_products (
        id SERIAL PRIMARY KEY,
        product_key TEXT UNIQUE,
        product_name TEXT NOT NULL,
        geo TEXT NOT NULL,
        source TEXT DEFAULT 'Meta Ads',
        page_name TEXT,
        media_type TEXT,
        ad_library_url TEXT,
        ad_snapshot_url TEXT,
        creative_preview_url TEXT,
        advertisers_count INTEGER DEFAULT 0,
        ads_count INTEGER DEFAULT 0,
        avg_days INTEGER DEFAULT 0,
        avg_price REAL DEFAULT 0,
        est_cost REAL DEFAULT 0,
        margin_percent INTEGER DEFAULT 0,
        competition TEXT,
        potential TEXT,
        recommendation TEXT,
        torito_score INTEGER DEFAULT 0,
        score_label TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("ALTER TABLE meta_ads_products ADD COLUMN IF NOT EXISTS page_name TEXT")
    cursor.execute("ALTER TABLE meta_ads_products ADD COLUMN IF NOT EXISTS media_type TEXT")
    cursor.execute("ALTER TABLE meta_ads_products ADD COLUMN IF NOT EXISTS ad_library_url TEXT")
    cursor.execute("ALTER TABLE meta_ads_products ADD COLUMN IF NOT EXISTS ad_snapshot_url TEXT")
    cursor.execute("ALTER TABLE meta_ads_products ADD COLUMN IF NOT EXISTS creative_preview_url TEXT")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meta_ads_cache_state (
        geo TEXT PRIMARY KEY,
        last_ingest_at TIMESTAMP,
        status TEXT,
        notes TEXT
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


def get_user_limits(user_id):
    info = get_user_referral_info(user_id)
    referrals_count = info["referrals_count"]
    total_limit = BASE_FREE_LIMIT + referrals_count * REFERRAL_BONUS_PER_FRIEND

    return {
        "base_limit": BASE_FREE_LIMIT,
        "referrals_count": referrals_count,
        "bonus_per_friend": REFERRAL_BONUS_PER_FRIEND,
        "total_limit": total_limit
    }


from datetime import date

def track_usage(user_id):
    ensure_usage_table()

    conn = get_connection()
    cursor = conn.cursor()

    today = date.today()

    cursor.execute("""
    INSERT INTO usage_daily (user_id, usage_date, count)
    VALUES (%s, %s, 1)
    ON CONFLICT (user_id, usage_date)
    DO UPDATE SET count = usage_daily.count + 1
    """, (user_id, today))

    conn.commit()
    conn.close()


def get_usage_today(user_id):
    ensure_usage_table()

    conn = get_connection()
    cursor = conn.cursor()

    today = date.today()

    cursor.execute("""
    SELECT count FROM usage_daily
    WHERE user_id = %s AND usage_date = %s
    """, (user_id, today))

    row = cursor.fetchone()
    conn.close()

    if row:
        return row[0]
    return 0


from datetime import date

def ensure_usage_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usage_daily (
        user_id BIGINT,
        usage_date DATE,
        count INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, usage_date)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meta_ads_raw (
        id SERIAL PRIMARY KEY,
        ad_id TEXT UNIQUE,
        geo TEXT NOT NULL,
        page_name TEXT,
        ad_text TEXT,
        landing_url TEXT,
        snapshot_url TEXT,
        start_date TIMESTAMP,
        active_days INTEGER DEFAULT 0,
        raw_payload JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meta_ads_products (
        id SERIAL PRIMARY KEY,
        product_key TEXT UNIQUE,
        product_name TEXT NOT NULL,
        geo TEXT NOT NULL,
        source TEXT DEFAULT 'Meta Ads',
        page_name TEXT,
        media_type TEXT,
        ad_library_url TEXT,
        ad_snapshot_url TEXT,
        creative_preview_url TEXT,
        advertisers_count INTEGER DEFAULT 0,
        ads_count INTEGER DEFAULT 0,
        avg_days INTEGER DEFAULT 0,
        avg_price REAL DEFAULT 0,
        est_cost REAL DEFAULT 0,
        margin_percent INTEGER DEFAULT 0,
        competition TEXT,
        potential TEXT,
        recommendation TEXT,
        torito_score INTEGER DEFAULT 0,
        score_label TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("ALTER TABLE meta_ads_products ADD COLUMN IF NOT EXISTS page_name TEXT")
    cursor.execute("ALTER TABLE meta_ads_products ADD COLUMN IF NOT EXISTS media_type TEXT")
    cursor.execute("ALTER TABLE meta_ads_products ADD COLUMN IF NOT EXISTS ad_library_url TEXT")
    cursor.execute("ALTER TABLE meta_ads_products ADD COLUMN IF NOT EXISTS ad_snapshot_url TEXT")
    cursor.execute("ALTER TABLE meta_ads_products ADD COLUMN IF NOT EXISTS creative_preview_url TEXT")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meta_ads_cache_state (
        geo TEXT PRIMARY KEY,
        last_ingest_at TIMESTAMP,
        status TEXT,
        notes TEXT
    )
    """)

    conn.commit()
    conn.close()


def track_usage(user_id):
    ensure_usage_table()

    conn = get_connection()
    cursor = conn.cursor()

    today = date.today()

    cursor.execute("""
    INSERT INTO usage_daily (user_id, usage_date, count)
    VALUES (%s, %s, 1)
    ON CONFLICT (user_id, usage_date)
    DO UPDATE SET count = usage_daily.count + 1
    """, (user_id, today))

    conn.commit()
    conn.close()


def get_usage_today(user_id):
    ensure_usage_table()

    conn = get_connection()
    cursor = conn.cursor()

    today = date.today()

    cursor.execute("""
    SELECT count FROM usage_daily
    WHERE user_id = %s AND usage_date = %s
    """, (user_id, today))

    row = cursor.fetchone()
    conn.close()

    if row:
        return row[0]
    return 0


def save_meta_ads_raw(records):
    if not records:
        return

    conn = get_connection()
    cursor = conn.cursor()

    for r in records:
        cursor.execute("""
        INSERT INTO meta_ads_raw (
            ad_id, geo, page_name, ad_text, landing_url, snapshot_url,
            start_date, active_days, raw_payload
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (ad_id) DO UPDATE SET
            geo = EXCLUDED.geo,
            page_name = EXCLUDED.page_name,
            ad_text = EXCLUDED.ad_text,
            landing_url = EXCLUDED.landing_url,
            snapshot_url = EXCLUDED.snapshot_url,
            start_date = EXCLUDED.start_date,
            active_days = EXCLUDED.active_days,
            raw_payload = EXCLUDED.raw_payload
        """, (
            r.get("ad_id"),
            r.get("geo"),
            r.get("page_name"),
            r.get("ad_text"),
            r.get("landing_url"),
            r.get("snapshot_url"),
            r.get("start_date"),
            r.get("active_days", 0),
            json.dumps(r)
        ))

    conn.commit()
    conn.close()


def save_meta_ads_products(records):
    if not records:
        return

    conn = get_connection()
    cursor = conn.cursor()

    for r in records:
        cursor.execute("""
        INSERT INTO meta_ads_products (
            product_key, product_name, geo, source,
            page_name, media_type, ad_library_url, ad_snapshot_url, creative_preview_url,
            advertisers_count, ads_count, avg_days,
            avg_price, est_cost, margin_percent,
            competition, potential, recommendation,
            torito_score, score_label, updated_at
        )
        VALUES (
            %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, CURRENT_TIMESTAMP
        )
        ON CONFLICT (product_key) DO UPDATE SET
            product_name = EXCLUDED.product_name,
            geo = EXCLUDED.geo,
            source = EXCLUDED.source,
            page_name = EXCLUDED.page_name,
            media_type = EXCLUDED.media_type,
            ad_library_url = EXCLUDED.ad_library_url,
            ad_snapshot_url = EXCLUDED.ad_snapshot_url,
            creative_preview_url = EXCLUDED.creative_preview_url,
            advertisers_count = EXCLUDED.advertisers_count,
            ads_count = EXCLUDED.ads_count,
            avg_days = EXCLUDED.avg_days,
            avg_price = EXCLUDED.avg_price,
            est_cost = EXCLUDED.est_cost,
            margin_percent = EXCLUDED.margin_percent,
            competition = EXCLUDED.competition,
            potential = EXCLUDED.potential,
            recommendation = EXCLUDED.recommendation,
            torito_score = EXCLUDED.torito_score,
            score_label = EXCLUDED.score_label,
            updated_at = CURRENT_TIMESTAMP
        """, (
            r.get("product_key"),
            r.get("product_name"),
            r.get("geo"),
            r.get("source", "Meta Ads"),
            r.get("page_name"),
            r.get("media_type"),
            r.get("ad_library_url"),
            r.get("ad_snapshot_url"),
            r.get("creative_preview_url"),
            r.get("advertisers_count", 0),
            r.get("ads_count", 0),
            r.get("avg_days", 0),
            r.get("avg_price", 0),
            r.get("est_cost", 0),
            r.get("margin_percent", 0),
            r.get("competition"),
            r.get("potential"),
            r.get("recommendation"),
            r.get("torito_score", 0),
            r.get("score_label"),
        ))

    conn.commit()
    conn.close()


def get_meta_ads_products_by_geo(geo, limit=10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        product_name,
        geo,
        source,
        page_name,
        media_type,
        ad_library_url,
        ad_snapshot_url,
        creative_preview_url,
        advertisers_count,
        ads_count,
        avg_days,
        avg_price,
        est_cost,
        margin_percent,
        competition,
        potential,
        recommendation,
        torito_score,
        score_label
    FROM meta_ads_products
    WHERE geo = %s
    ORDER BY torito_score DESC, avg_days DESC, advertisers_count DESC
    LIMIT %s
    """, (geo.lower(), limit))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "name": row[0],
            "geo": row[1],
            "source": row[2],
            "page_name": row[3],
            "media_type": row[4],
            "ad_library_url": row[5],
            "ad_snapshot_url": row[6],
            "creative_preview_url": row[7],
            "advertisers_count": row[8],
            "ads_count": row[9],
            "days": row[10],
            "price": row[11],
            "cost": row[12],
            "margin": row[13],
            "competition": row[14],
            "potential": row[15],
            "recommendation": row[16],
            "score": row[17],
            "score_label": row[18],
        }
        for row in rows
    ]


def update_meta_ads_cache_state(geo, status, notes=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO meta_ads_cache_state (geo, last_ingest_at, status, notes)
    VALUES (%s, CURRENT_TIMESTAMP, %s, %s)
    ON CONFLICT (geo) DO UPDATE SET
        last_ingest_at = CURRENT_TIMESTAMP,
        status = EXCLUDED.status,
        notes = EXCLUDED.notes
    """, (geo.lower(), status, notes))

    conn.commit()
    conn.close()


def get_meta_ads_cache_state(geo):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT geo, last_ingest_at, status, notes
    FROM meta_ads_cache_state
    WHERE geo = %s
    """, (geo.lower(),))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "geo": row[0],
        "last_ingest_at": row[1],
        "status": row[2],
        "notes": row[3],
    }
