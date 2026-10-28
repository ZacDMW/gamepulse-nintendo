"""Check official Nintendo investor pages for a newly reported reporting date.

Deliberately does not scrape and auto-publish partial data or infer sales.
Official site layout can change, and updated dates require manual validation
before adding a complete snapshot to data/snapshot.json.
"""
import json
import re
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / 'data' / 'snapshot.json'
URLS = [
    'https://www.nintendo.co.jp/ir/en/finance/hard_soft/index.html',
    'https://www.nintendo.co.jp/ir/en/finance/software/index.html',
]
DATE_PATTERN = re.compile(r'As of\s+([A-Za-z]+\s+\d{1,2},\s+20\d{2})', re.IGNORECASE)


def reporting_date(html):
    text = BeautifulSoup(html, 'html.parser').get_text(' ', strip=True)
    match = DATE_PATTERN.search(text)
    return datetime.strptime(match.group(1), '%B %d, %Y').date().isoformat() if match else None


def check_for_updates():
    saved = json.loads(SEED.read_text(encoding='utf-8'))['as_of']
    observed = []
    for url in URLS:
        response = requests.get(url, timeout=20, headers={'User-Agent':'GamePulseResearch/0.1 (portfolio educational project)'})
        response.raise_for_status()
        observed.append((url, reporting_date(response.text)))
    for url, date in observed:
        print(f'{url}: reported {date or "UNKNOWN"} (saved {saved})')
    if any(date is None for _, date in observed):
        raise RuntimeError('Could not verify reporting dates; manual review required')
    if len({date for _, date in observed}) != 1:
        raise RuntimeError('Sources show different reporting dates; manual review required')
    if observed[0][1] > saved:
        print('NEW REPORT AVAILABLE: manually verify and append a complete new snapshot before publishing.')
    else:
        print('Seed snapshot is current for these page dates; no data changed.')


if __name__ == '__main__':
    check_for_updates()
