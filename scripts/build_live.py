#!/usr/bin/env python3
"""Build normalized live-event JSON and the static GitHub Pages HTML page."""
from pathlib import Path
import html
import json

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "live.yml"
OUT_JSON = ROOT / "data" / "tokyo-live.json"
OUT_HTML = ROOT / "docs" / "tokyo-theaters.html"


def main():
    source = yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}
    theaters = source.get("theaters", [])
    events = source.get("events", [])

    payload = {
        "schema": "yoshimoto-theater/live-v1",
        "generated_from": "config/live.yml",
        "theaters": theaters,
        "events": events,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    by_theater = {t.get("id"): t for t in theaters}
    groups = {}
    for event in events:
        groups.setdefault(event.get("theater_id", "unknown"), []).append(event)

    parts = [
        "<!doctype html>",
        '<html lang="ja"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<title>東京ライブチェック</title>',
        '<style>body{font-family:system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem}section{margin:2rem 0}li{margin:.5rem 0}.meta{color:#666;font-size:.9em}</style>',
        "</head><body>",
        "<h1>東京ライブチェック</h1>",
    ]
    for theater_id, theater_events in groups.items():
        theater = by_theater.get(theater_id, {})
        name = html.escape(theater.get("name", theater_id))
        area = html.escape(theater.get("area", ""))
        parts.append(f'<section><h2>{name}</h2><p class="meta">{area}</p><ul>')
        for event in sorted(theater_events, key=lambda x: (x.get("date", ""), x.get("start", ""))):
            title = html.escape(event.get("title", ""))
            date = html.escape(event.get("date", ""))
            start = html.escape(event.get("start", ""))
            parts.append(f"<li><strong>{date} {start}</strong> — {title}</li>")
        parts.append("</ul></section>")
    parts += [
        '<p><a href="data/tokyo-live.json">JSON</a> · <a href="data/theaters.jsonl">劇場マスター</a></p>',
        "</body></html>",
    ]
    OUT_HTML.write_text("\n".join(parts) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
