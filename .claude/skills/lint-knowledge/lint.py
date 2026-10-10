#!/usr/bin/env python3
"""Механические проверки базы знаний. Только чтение, ничего не исправляет.

Запуск из корня репозитория:
    python3 .claude/skills/lint-knowledge/lint.py [--today YYYY-MM-DD] [--stale-months N]

Код выхода: 1 — есть 🔴, 0 — нет.
Смысловые проверки (противоречия, непомеченные утверждения) делает агент по SKILL.md:
скрипт выдаёт ему только инвентарь мест, где один и тот же факт повторяется.
"""

import argparse
import datetime as dt
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

VALID_TAGS = {"норма", "официальное разъяснение", "практика", "не подтверждено"}

# Файлы, которые живут только в my-data/ и упоминаются по имени без пути.
PRIVATE_NAMES = {
    "profile.yaml", "data.yaml", "open-issues.md", "worksheet.md", "debts.md",
    "inmovilizado.md", "summary.md", "audit.md", "libros-notas.md", "README.md",
    "SKILL.md",
}

# Где искать файл, упомянутый голым именем.
BARE_SEARCH_DIRS = ["knowledge", "templates", "examples", "."]

FENCE = re.compile(r"^\s*(```|~~~)")
HEADER_DATE = re.compile(r"^>\s*Актуально на:\s*(\d{4})-(\d{2})")
CODE_REF = re.compile(r"`([\w./-]+\.(?:md|ya?ml|py))(#[^`\s]*)?(?::\d+)?`")
MD_LINK = re.compile(r"\]\(([^)\s]+)\)")
# Любой тег с кириллицей: ловит и смешанные раскладки вроде «нормa» с латинской a.
TAG = re.compile(r"`\[([^\]`]*[а-яё][^\]`]*)\]`")
SECTION_REF = re.compile(r"раздел[а-я]*\s+«([^»]+)»")
ANY_FILE = re.compile(r"([\w./-]+\.md)")
NORM_ANCHOR = re.compile(r"\bart(?:s|ículo)?\.?\s*\d|\bBOE\b|\bRD\s*\d|\bLey\s*\d|\bOrden\b|\bLIRPF\b|\bLIVA\b|\bLGT\b|\bRGAT\b|\bRIRPF\b", re.I)
CASILLA = re.compile(r"casillas?\s+\d+", re.I)

PRIVACY = [
    ("DNI", re.compile(r"\b\d{8}-?[A-HJ-NP-TV-Z]\b")),
    ("NIE", re.compile(r"\b[XYZ]-?\d{7}-?[A-Z]\b")),
    ("IBAN", re.compile(r"\bES\d{2}(?:[ ]?\d{4}){5}\b")),
    ("e-mail", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")),
    ("13-значный номер (justificante?)", re.compile(r"\b\d{13}\b")),
]
PRIVACY_ALLOW = {"noreply@anthropic.com"}

PERCENT = re.compile(r"(?<![\d,.])(\d{1,3}(?:[,.]\d+)?)\s?%")
EURO = re.compile(r"(?<![\d,.])(\d{1,3}(?:[ .]\d{3})*(?:,\d{1,2})?)\s?€")
ACT = re.compile(r"\b(?:RD|Real Decreto(?:-ley)?|RDL|Ley|Orden(?: HAC| HFP)?)\s*(\d+/\d{4})")
YEAR = re.compile(r"\b(20\d{2})\b")
YEAR_SENSITIVE = re.compile(r"€|%|cuota|límite|limite|лимит|тариф|base mínima|tope", re.I)


class Report:
    def __init__(self):
        self.items = defaultdict(list)  # (level, check) -> [msg]

    def add(self, level, check, msg):
        self.items[(level, check)].append(msg)

    def count(self, level):
        return sum(len(v) for (lv, _), v in self.items.items() if lv == level)

    def print(self, inventory):
        icons = {"E": "🔴", "W": "🟡"}
        for level in ("E", "W"):
            checks = [(c, m) for (lv, c), m in self.items.items() if lv == level]
            if not checks:
                continue
            print(f"\n{icons[level]} {'Ошибки' if level == 'E' else 'Проверить'}")
            for check, msgs in sorted(checks):
                print(f"\n  ## {check} ({len(msgs)})")
                for m in msgs:
                    print(f"  - {m}")
        print("\n🟢 Инвентарь для смысловой проверки")
        for title, lines in inventory:
            print(f"\n  ## {title}")
            if not lines:
                print("  (пусто)")
            for line in lines:
                print(f"  {line}")
        print(f"\nИтого: 🔴 {self.count('E')} · 🟡 {self.count('W')}")


def public_files():
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.split("\n")
    return sorted(ROOT / p for p in out if p and (ROOT / p).is_file())


def unfenced(text):
    """(номер строки, строка) вне блоков кода."""
    inside = False
    for i, line in enumerate(text.split("\n"), 1):
        if FENCE.match(line):
            inside = not inside
            continue
        if not inside:
            yield i, line


def slug(heading):
    h = re.sub(r"[^\w\- ]", "", heading.strip().lower())
    return h.replace(" ", "-")


def headings(path):
    hs = []
    for _, line in unfenced(path.read_text(encoding="utf-8")):
        m = re.match(r"^#{1,6}\s+(.*)", line)
        if m:
            hs.append(m.group(1).strip())
    return hs


def rel(p):
    return str(p.relative_to(ROOT))


def resolve(ref, src):
    """Путь из ссылки → Path или None. 'skip' — ссылка не проверяется."""
    if ref.startswith(("http://", "https://", "mailto:")):
        return "skip"
    if "my-data" in ref or any(ch in ref for ch in "<[*{"):
        return "skip"
    if "/" in ref:
        for base in (src.parent, ROOT):
            p = (base / ref).resolve()
            if p.exists():
                return p
        return None
    for d in [src.parent] + [ROOT / x for x in BARE_SEARCH_DIRS]:
        p = d / ref
        if p.exists():
            return p.resolve()
    if ref in PRIVATE_NAMES:
        return "skip"
    return None


def check_header(path, text, today, stale_months, r):
    head = text.split("\n")[:10]
    date = None
    for line in head:
        m = HEADER_DATE.match(line)
        if m:
            date = (int(m.group(1)), int(m.group(2)))
    name = rel(path)
    if not date:
        r.add("E", "Нет строки «> Актуально на: ГГГГ-ММ» в шапке", name)
    else:
        age = (today.year - date[0]) * 12 + today.month - date[1]
        if age > stale_months:
            r.add("W", f"«Актуально на» старше {stale_months} мес.", f"{name}: {date[0]}-{date[1]:02d} ({age} мес.)")
        if age < 0:
            r.add("E", "«Актуально на» в будущем", f"{name}: {date[0]}-{date[1]:02d}")
    if not any(l.startswith("> Перепроверять:") for l in head):
        r.add("W", "Нет строки «> Перепроверять:» в шапке", name)
    if len(CASILLA.findall(text)) >= 3 and not any(re.search(r"casillas.*20\d\d|20\d\d.*casillas", l) for l in head):
        r.add("W", "Много номеров casillas, но в шапке не указан год формы", name)


def check_links(path, text, r, incoming):
    lines = text.split("\n")
    for n, line in unfenced(text):
        # Путь рядом со ссылкой на GitHub — файл чужого репозитория, не наш.
        external = "github.com" in "\n".join(lines[max(0, n - 3): n + 2])
        refs = [(m.group(1), m.group(2)) for m in CODE_REF.finditer(line)]
        for m in MD_LINK.finditer(line):
            target = m.group(1)
            if target.startswith("#"):
                refs.append(("", target))
            else:
                f, _, a = target.partition("#")
                refs.append((f, "#" + a if a else None))
        for ref, anchor in refs:
            target = path if ref == "" else resolve(ref, path)
            if target == "skip":
                continue
            if target is None and external:
                continue
            if target is None:
                r.add("E", "Битая ссылка на файл", f"{rel(path)}:{n} → `{ref}`")
                continue
            if target != path:
                incoming[target].add(path)
            if anchor and target.suffix == ".md":
                slugs = {slug(h) for h in headings(target)}
                if anchor[1:].lower() not in slugs:
                    r.add("E", "Битый якорь (#раздел)", f"{rel(path)}:{n} → `{ref}{anchor}`")
        for m in SECTION_REF.finditer(line):
            # Файл раздела — ближайший слева на строке, иначе первый справа (до конца
            # следующей строки), иначе текущий файл.
            before = ANY_FILE.findall(line[: m.start()])
            after = ANY_FILE.findall(line[m.end():] + " " + (lines[n] if n < len(lines) else ""))
            ref = before[-1] if before else after[0] if after else None
            target = resolve(ref, path) if ref else path
            if target in (None, "skip"):
                continue
            want = m.group(1).lower()
            if not any(want in h.lower() for h in headings(target)):
                r.add("E", "Ссылка на несуществующий раздел «…»", f"{rel(path)}:{n} → {rel(target)} «{m.group(1)}»")


def check_tags(path, text, r):
    lines = text.split("\n")
    for n, line in unfenced(text):
        for m in TAG.finditer(line):
            tag = m.group(1)
            if tag not in VALID_TAGS:
                r.add("E", "Неизвестный тег достоверности", f"{rel(path)}:{n} `[{tag}]`")
            elif tag == "норма" and claims_file(path):
                window = "\n".join(lines[max(0, n - 4): n + 4])
                if not NORM_ANCHOR.search(window):
                    r.add("W", "`[норма]` без статьи/акта рядом (±3 строки)", f"{rel(path)}:{n}")


def claims_file(path):
    """Файлы, где теги — утверждения, а не описание самой шкалы."""
    top = path.relative_to(ROOT).parts[0]
    return top in {"knowledge", "templates", "examples"} and path.name != "sources-primarias.md"


def check_privacy(path, text, r):
    for n, line in enumerate(text.split("\n"), 1):
        for label, rx in PRIVACY:
            for m in rx.finditer(line):
                if m.group(0) in PRIVACY_ALLOW:
                    continue
                r.add("E", "Похоже на личные данные в публичном файле", f"{rel(path)}:{n} {label}: {m.group(0)}")


def check_index(knowledge, r, incoming):
    claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    for p in knowledge:
        if f"knowledge/{p.name}" not in claude:
            r.add("E", "Файл knowledge/ не внесён в карту в CLAUDE.md", rel(p))
        others = {s for s in incoming[p.resolve()] if s.name != "CLAUDE.md"}
        if not others:
            r.add("W", "На файл ссылается только CLAUDE.md (нет входящих ссылок из базы и skills)", rel(p))
    for name in re.findall(r"`knowledge/([\w.-]+\.md)`", claude):
        if not (ROOT / "knowledge" / name).exists():
            r.add("E", "Карта в CLAUDE.md ссылается на несуществующий файл", f"knowledge/{name}")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for d in sorted((ROOT / ".claude" / "skills").iterdir()):
        if (d / "SKILL.md").exists() and f"/{d.name}" not in readme:
            r.add("W", "Skill не упомянут в README.md", d.name)


def inventory(knowledge, claims, today):
    pct, eur = defaultdict(set), defaultdict(set)
    years = []
    anchors = set(ACT.findall((ROOT / "knowledge" / "sources-primarias.md").read_text(encoding="utf-8")))
    acts = defaultdict(set)
    for p in claims:
        for n, line in unfenced(p.read_text(encoding="utf-8")):
            for act in ACT.findall(line):
                if act not in anchors:
                    acts[act].add(f"{rel(p)}:{n}")
    for p in knowledge:
        text = p.read_text(encoding="utf-8")
        for n, line in unfenced(text):
            for m in PERCENT.finditer(line):
                pct[m.group(1).replace(".", ",")].add(f"{p.name}:{n}")
            for m in EURO.finditer(line):
                eur[m.group(1)].add(f"{p.name}:{n}")
            if YEAR_SENSITIVE.search(line):
                old = [y for y in YEAR.findall(line) if int(y) < today.year]
                if old and n > 10:
                    years.append(f"{p.name}:{n} ({', '.join(sorted(set(old)))}): {line.strip()[:110]}")

    def multi(d, unit):
        out = []
        for val, locs in sorted(d.items(), key=lambda kv: -len({l.split(':')[0] for l in kv[1]})):
            files = {l.split(":")[0] for l in locs}
            if len(files) >= 2:
                out.append(f"{val} {unit} — {len(files)} файлов: {', '.join(sorted(locs))}")
        return out

    return [
        ("Проценты, встречающиеся в 2+ файлах (сверить, что значат одно и то же)", multi(pct, "%")),
        ("Суммы в €, встречающиеся в 2+ файлах", multi(eur, "€")),
        (f"Строки с суммами/ставками и годом < {today.year} (не устарели ли)", years),
        ("Акты, которых нет в sources-primarias.md (изменяющий акт или вне охвата — ок; "
         "опора для утверждения — добавить якорь)",
         [f"{a}: {', '.join(sorted(l))}" for a, l in sorted(acts.items())]),
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", type=dt.date.fromisoformat, default=dt.date.today())
    ap.add_argument("--stale-months", type=int, default=6)
    a = ap.parse_args()

    r = Report()
    files = public_files()
    md = [p for p in files if p.suffix == ".md"]
    knowledge = [p for p in md if p.parent == ROOT / "knowledge"]
    incoming = defaultdict(set)

    for p in knowledge:
        check_header(p, p.read_text(encoding="utf-8"), a.today, a.stale_months, r)
    for p in md:
        text = p.read_text(encoding="utf-8")
        check_links(p, text, r, incoming)
        check_tags(p, text, r)
    for p in files:
        if p.suffix in {".md", ".yaml", ".yml", ".py", ".json"}:
            check_privacy(p, p.read_text(encoding="utf-8"), r)
    check_index(knowledge, r, incoming)

    print(f"LINT базы знаний · {a.today.isoformat()} · файлов: {len(files)}, из них knowledge/: {len(knowledge)}")
    claims = [p for p in md if claims_file(p) or ".claude" in p.parts]
    r.print(inventory(knowledge, claims, a.today))
    return 1 if r.count("E") else 0


if __name__ == "__main__":
    sys.exit(main())
