import os
from datetime import datetime

import psycopg2
import psycopg2.extras


def _get_database_url():
    """
    Vercel's Neon (Postgres) integration injects DATABASE_URL automatically.
    Some older docs/integrations use POSTGRES_URL instead, so we fall back
    to that if DATABASE_URL isn't present.
    """
    url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL (or POSTGRES_URL) is not set. Add a Postgres "
            "database to this project from the Vercel Storage tab, or set "
            "the variable manually in Settings > Environment Variables."
        )
    # psycopg2 wants "postgresql://", but some providers hand out "postgres://"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


def get_connection():
    conn = psycopg2.connect(_get_database_url(), sslmode="require")
    return conn


def init_db():
    """Create the reservations table if it doesn't exist yet."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            service TEXT NOT NULL,
            message TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


def get_booked_times_for_today():
    """Return a set of time-slot strings that are already taken today (active only)."""
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT time FROM reservations WHERE date = %s AND status = 'active'",
        (today,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {row[0] for row in rows}


def is_slot_taken(date, time):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM reservations WHERE date = %s AND time = %s AND status = 'active'",
        (date, time)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row is not None


def create_reservation(name, phone, date, time, service, message):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO reservations (name, phone, date, time, service, message, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, 'active', %s)
    """, (name, phone, date, time, service, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    cur.close()
    conn.close()


def get_all_reservations():
    """Return all reservations, most recent first, for the admin dashboard."""
    conn = get_connection()
    # RealDictCursor makes rows behave like dicts (r['name'], r['id'], etc.)
    # so admin.html's {{ r['date'] }} style access keeps working unchanged.
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "SELECT * FROM reservations ORDER BY date DESC, created_at DESC"
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def cancel_reservation(reservation_id):
    """Mark a reservation cancelled, which frees up that slot again."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE reservations SET status = 'cancelled' WHERE id = %s",
        (reservation_id,)
    )
    conn.commit()
    cur.close()
    conn.close()


# MONTH / DAY DRILL-DOWN

def get_monthly_summary():
    """Return rows of {month: 'YYYY-MM', count: N} for every month that has reservations."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT substr(date, 1, 7) AS month, COUNT(*) AS count
        FROM reservations
        GROUP BY month
        ORDER BY month DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_daily_summary(month):
    """Return rows of {date: 'YYYY-MM-DD', count: N} for every day in the given month (YYYY-MM)."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT date, COUNT(*) AS count
        FROM reservations
        WHERE substr(date, 1, 7) = %s
        GROUP BY date
        ORDER BY date ASC
    """, (month,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_reservations_for_date(date):
    """Return every reservation (active + cancelled) made for a specific date."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "SELECT * FROM reservations WHERE date = %s ORDER BY created_at ASC",
        (date,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
