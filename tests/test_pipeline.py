import json
import sqlite3
from pathlib import Path
from src.database import initialize, insert_snapshot
from src.refresh import reporting_date


def test_date_detection():
    assert reporting_date('<p>( As of June 30, 2026 )</p>') == '2026-06-30'
    assert reporting_date('<p>no date</p>') is None


def test_snapshot_idempotent():
    record=json.loads((Path(__file__).parents[1]/'data'/'snapshot.json').read_text())
    with sqlite3.connect(':memory:') as connection:
        initialize(connection)
        insert_snapshot(connection, record)
        insert_snapshot(connection, record)
        assert connection.execute('SELECT count(*) FROM consoles').fetchone()[0] == len(record['consoles'])
        assert connection.execute('SELECT count(*) FROM titles').fetchone()[0] == len(record['titles'])
