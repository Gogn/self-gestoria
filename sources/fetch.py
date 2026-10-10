#!/usr/bin/env python3
"""Скачивает выдержки первоисточников по sources/manifest.json и пишет их в sources/.

Запуск из корня репозитория:
    python3 -I sources/fetch.py            # все файлы манифеста
    python3 -I sources/fetch.py boe/lis.md # только указанные

Текст берётся программно (API консолидированного законодательства BOE, HTML AEAT), а не
пересказом модели. Поэтому файлы в sources/ руками не правятся: только перезапуском.
Только stdlib. Скачанное — чужие данные: в файл идёт лишь извлечённый текст.
"""

import datetime as dt
import hashlib
import html.parser
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOE_API = "https://www.boe.es/datosabiertos/api/legislacion-consolidada/id/{norm}/texto/bloque/{block}"
BOE_PAGE = "https://www.boe.es/buscar/act.php?id={norm}"


def get(url, accept):
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "Mozilla/5.0 self-gestoria/fetch"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def text_of(el):
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip()


def ymd(s):
    return f"{s[:4]}-{s[4:6]}-{s[6:]}"


def slice_lines(lines, start, end):
    """Строки от первой, начинающейся со start, до первой, начинающейся с end (не включая)."""
    if not start:
        return lines
    i = next(k for k, l in enumerate(lines) if l.lstrip("#> ").startswith(start))
    if not end:
        return lines[i:]
    j = next(k for k in range(i + 1, len(lines)) if lines[k].lstrip("#> ").startswith(end))
    return lines[i:j]


def boe_block(norm, block, today):
    root = ET.fromstring(get(BOE_API.format(norm=norm, block=block), "application/xml"))
    if root.findtext("status/code") != "200":
        raise SystemExit(f"BOE {norm}/{block}: {root.findtext('status/text')}")
    b = root.find("data/bloque")
    versions = [v for v in b.findall("version") if v.get("fecha_vigencia", "0") <= today.strftime("%Y%m%d")]
    v = versions[-1]
    lines = []
    for p in v.iter("p"):
        t = text_of(p)
        if not t:
            continue
        cls = p.get("class", "")
        if cls == "articulo" or cls.startswith("titulo"):
            lines.append(f"### {t}")
        elif cls == "nota_pie":
            lines.append(f"> {t}")
        else:
            lines.append(t)
    meta = f"блок `{block}` ({b.get('titulo')}): редакция в силе с {ymd(v.get('fecha_vigencia'))}, внесена {v.get('id_norma')}"
    return lines, meta


class Text(html.parser.HTMLParser):
    BLOCK = {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "br", "tr", "section", "article", "main"}

    def __init__(self):
        super().__init__()
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip -= 1
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

    def lines(self):
        return [re.sub(r"\s+", " ", l).strip() for l in "".join(self.parts).split("\n") if l.strip()]


def html_page(url):
    p = Text()
    p.feed(get(url, "text/html"))
    lines = p.lines()
    updated = next((lines[k + 1] if l.rstrip().endswith(":") else l.split(":", 1)[1].strip()
                    for k, l in enumerate(lines) if l.lower().startswith("página actualizada")
                    or l.lower().startswith("actualizada")), "не найдена")
    return lines, updated


def body_hash(text):
    """Хеш текста под шапкой. Тот же алгоритм в lint.py: ручная правка его ломает."""
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()[:16]


def build(entry, today):
    body, meta = [], []
    if entry["type"] == "boe":
        for block in entry["blocks"]:
            lines, m = boe_block(entry["norm"], block, today)
            lines = slice_lines(lines, entry.get("start"), entry.get("end"))
            body += lines + [""]
            meta.append(m)
        source = BOE_PAGE.format(norm=entry["norm"])
        reuse = "Текст нормативного акта (Ley de Propiedad Intelectual, art. 13 — не объект авторского права)."
    else:
        lines, updated = html_page(entry["url"])
        body = slice_lines(lines, entry["start"], entry["end"])
        source = entry["url"]
        meta.append(f"страница AEAT обновлена: {updated}")
        reuse = ("Повторное использование разрешено AEAT при указании источника и даты обновления, "
                 "без искажения содержания (Aviso legal → Utilización de la información).")
    digest = body_hash("\n".join(body))
    head = [
        f"# {entry['title']}",
        "",
        f"> Источник: {source}",
        f"> Снято: {today.isoformat()} скриптом `sources/fetch.py` — **вручную не править**.",
    ] + [f"> {m}" for m in meta] + [f"> {reuse}", f"> Контроль: sha256 текста `{digest}` — сверяет /lint-knowledge.", ""]
    return "\n".join(head + body).rstrip() + "\n"


def main():
    today = dt.date.today()
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    only = set(sys.argv[1:])
    for entry in manifest["files"]:
        if only and entry["file"] not in only:
            continue
        out = HERE / entry["file"]
        out.parent.mkdir(parents=True, exist_ok=True)
        text = build(entry, today)
        strip = lambda t: [l for l in t.splitlines() if not l.startswith("> Снято:")]
        changed = not out.exists() or strip(out.read_text(encoding="utf-8")) != strip(text)
        out.write_text(text, encoding="utf-8")
        print(f"{entry['file']}: {len(text.splitlines())} строк{' — ИЗМЕНИЛСЯ' if changed else ''}")


if __name__ == "__main__":
    main()
