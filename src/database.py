"""Small, auditable SQLite storage for Nintendo quarterly sales snapshots."""
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "gamepulse.sqlite3"
SEED = ROOT / "data" / "snapshot.json"


def connect(path=DB):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS snapshots (
      as_of TEXT PRIMARY KEY, source_hardware TEXT NOT NULL,
      source_titles TEXT NOT NULL, collected_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS consoles (
      as_of TEXT NOT NULL, name TEXT NOT NULL, hardware_m REAL NOT NULL,
      software_m REAL NOT NULL, PRIMARY KEY(as_of, name),
      FOREIGN KEY(as_of) REFERENCES snapshots(as_of)
    );
    CREATE TABLE IF NOT EXISTS titles (
      as_of TEXT NOT NULL, platform TEXT NOT NULL, title TEXT NOT NULL,
      genre TEXT NOT NULL, units_m REAL NOT NULL, note TEXT NOT NULL,
      PRIMARY KEY(as_of, platform, title),
      FOREIGN KEY(as_of) REFERENCES snapshots(as_of)
    );
    """)
    conn.commit()


def insert_snapshot(conn, record):
    """Validated historical observations; never overwrite a previously imported reporting date."""
    as_of = record['as_of']
    if not record['consoles'] or not record['titles']:
        raise ValueError('Incomplete snapshot; refusing to import')
    with conn:
        conn.execute('INSERT OR IGNORE INTO snapshots(as_of,source_hardware,source_titles) VALUES (?,?,?)',
                     (as_of, record['hardware_source'], record['software_source']))
        conn.executemany('INSERT OR IGNORE INTO consoles VALUES (?,?,?,?)',
                         [(as_of, x['name'], x['hardware_m'], x['software_m']) for x in record['consoles']])
        conn.executemany('INSERT OR IGNORE INTO titles VALUES (?,?,?,?,?,?)',
                         [(as_of, x['platform'], x['title'], x['genre'], x['units_m'], x['note']) for x in record['titles']])


def seed(conn):
    initialize(conn)
    insert_snapshot(conn, json.loads(SEED.read_text(encoding='utf-8')))


if __name__ == '__main__':
    with connect() as db:
        seed(db)
        print('Database ready:', DB)
