#!/usr/bin/env python3
"""
MyHP Content Builder Script
===========================
This script automatically parses plain text files in the `content/` folder
and updates `index.html`, `index_jp.html`, `about.html`, `about_jp.html`,
`research.html`, `research_jp.html`, and generates column HTML files.
"""

import os
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT_DIR / "content"
COLUMNS_DIR = CONTENT_DIR / "columns"


def read_text(file_path):
    if not file_path.exists():
        return ""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()


def write_text(file_path, content):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def parse_key_value_items(file_path):
    """Parses lines formatted as: Title / Date | Description"""
    raw = read_text(file_path)
    items = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "|" in line:
            title_part, desc_part = line.split("|", 1)
            items.append((title_part.strip(), desc_part.strip()))
    return items


def update_news(html_file, news_file):
    if not html_file.exists() or not news_file.exists():
        return
    news_items = parse_key_value_items(news_file)
    if not news_items:
        return

    html_lines = []
    for date, text in news_items:
        html_lines.append('                    <article class="news-item">')
        html_lines.append(f'                        <span class="news-date">{date}</span>')
        html_lines.append(f'                        <p class="news-content">{text}</p>')
        html_lines.append('                    </article>')
    news_html = "\n".join(html_lines)

    content = read_text(html_file)
    pattern = r'(<div class="news-scroll[^"]*">)(.*?)(</div>\s*</div>)'
    replacement = f'\\1\n{news_html}\n            \\3'
    updated, count = re.subn(pattern, replacement, content, flags=re.DOTALL)
    if count > 0:
        write_text(html_file, updated)
        print(f"[{html_file.name}] Successfully updated {len(news_items)} news entries from {news_file.name}")
    else:
        print(f"[{html_file.name}] WARNING: News section regex pattern did not match! File unchanged.")


def update_blue_horse(html_file, text_file):
    if not html_file.exists() or not text_file.exists():
        return
    text_content = read_text(text_file)
    if not text_content:
        return
    content = read_text(html_file)
    pattern = r'(<p class="modal-placeholder-text">)(.*?)(</p>)'
    replacement = f'\\1\n                    {text_content}\n                \\3'
    updated, count = re.subn(pattern, replacement, content, flags=re.DOTALL)
    if count > 0:
        write_text(html_file, updated)
        print(f"[{html_file.name}] Successfully updated Why Blue Horse text from {text_file.name}")
    else:
        print(f"[{html_file.name}] WARNING: Blue Horse modal regex pattern did not match! File unchanged.")


def update_list_section(html_file, text_file, section_h3_title):
    """Updates <ul> list in about.html under specific <h3> header"""
    if not html_file.exists() or not text_file.exists():
        return
    items = parse_key_value_items(text_file)
    if not items:
        return

    list_lines = []
    for title, desc in items:
        list_lines.append(f'                            <li><strong>{title}</strong>: {desc}</li>')
    list_html = "\n".join(list_lines)

    content = read_text(html_file)
    pattern = rf'(<h3>\s*{re.escape(section_h3_title)}\s*</h3>\s*<ul>)(.*?)(</ul>)'
    replacement = f'\\1\n{list_html}\n                        \\3'
    updated, count = re.subn(pattern, replacement, content, flags=re.DOTALL)
    if count > 0:
        write_text(html_file, updated)
        print(f"[{html_file.name}] Successfully updated '{section_h3_title}' section ({len(items)} items)")
    else:
        print(f"[{html_file.name}] WARNING: Section '{section_h3_title}' regex pattern did not match! File unchanged.")


def parse_column_file(file_path):
    raw = read_text(file_path)
    metadata = {}
    body = ""
    if "---" in raw:
        meta_part, body_part = raw.split("---", 1)
        body = body_part.strip()
        for line in meta_part.splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                metadata[key.strip().lower()] = val.strip()
    else:
        body = raw

    return {
        "title": metadata.get("title", "Untitled Column"),
        "date": metadata.get("date", "2026.04"),
        "tag": metadata.get("tag", "Column"),
        "summary": metadata.get("summary", ""),
        "body": body,
    }


def format_markdown_body(body_text):
    paragraphs = []
    for block in body_text.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        if block.startswith("###"):
            title_text = block.replace("###", "").strip()
            paragraphs.append(f"                    <h3>{title_text}</h3>")
        elif block.startswith("##"):
            title_text = block.replace("##", "").strip()
            paragraphs.append(f"                    <h2>{title_text}</h2>")
        else:
            paragraphs.append(f"                    <p>\n                        {block}\n                    </p>")
    return "\n\n".join(paragraphs)


def process_columns():
    if not COLUMNS_DIR.exists():
        return

    en_columns = []
    jp_columns = []

    for f in sorted(COLUMNS_DIR.glob("*.txt")):
        col_id = f.stem
        col_data = parse_column_file(f)

        if col_id.endswith("_jp"):
            base_id = col_id[:-3]
            target_html = ROOT_DIR / f"{base_id}_jp.html"
            jp_columns.append((base_id, col_data))
            generate_column_html(target_html, col_data, base_id, lang="jp")
        else:
            base_id = col_id[:-3] if col_id.endswith("_en") else col_id
            target_html = ROOT_DIR / f"{base_id}.html"
            en_columns.append((base_id, col_data))
            generate_column_html(target_html, col_data, base_id, lang="en")

    update_research_columns_list(ROOT_DIR / "research.html", en_columns, lang="en")
    update_research_columns_list(ROOT_DIR / "research_jp.html", jp_columns, lang="jp")


def update_research_columns_list(research_html_file, columns, lang="en"):
    if not research_html_file.exists() or not columns:
        return
    content = read_text(research_html_file)

    cards = []
    for base_id, data in columns:
        link_target = f"{base_id}_jp.html" if lang == "jp" else f"{base_id}.html"
        read_more_text = "コラムを読む →" if lang == "jp" else "Read Column →"
        cards.append(f"""                            <article class="column-item-card">
                                <div class="column-header-row">
                                    <span class="column-tag">{data['tag']}</span>
                                    <span class="column-date">{data['date']}</span>
                                </div>
                                <h4><a href="{link_target}">{data['title']}</a></h4>
                                <p class="column-summary">
                                    {data['summary']}
                                </p>
                                <a href="{link_target}" class="read-column-link">{read_more_text}</a>
                            </article>""")

    cards_html = "\n".join(cards)
    pattern = r'(<div class="columns-list">)(.*?)(</div>\s*</div>\s*</div>)'
    replacement = f'\\1\n{cards_html}\n                        \\3'
    updated, count = re.subn(pattern, replacement, content, flags=re.DOTALL)
    if count > 0:
        write_text(research_html_file, updated)
        print(f"[{research_html_file.name}] Successfully updated {len(columns)} column card(s)")
    else:
        print(f"[{research_html_file.name}] WARNING: Columns list regex pattern did not match! File unchanged.")


def generate_column_html(target_html, col_data, base_id, lang="en"):
    body_html = format_markdown_body(col_data["body"])
    lang_attr = "ja" if lang == "jp" else "en"
    switch_href = f"{base_id}.html" if lang == "jp" else f"{base_id}_jp.html"
    switch_label = "EN" if lang == "jp" else "JP"
    switch_title = "Switch to English" if lang == "jp" else "日本語ページへ"
    back_href = "research_jp.html" if lang == "jp" else "research.html"
    back_label = "← 研究一覧へ戻る" if lang == "jp" else "← Back to Research"
    return_label = "← 研究一覧に戻る" if lang == "jp" else "← Return to Research List"
    nav_home = "ホーム" if lang == "jp" else "Home"
    nav_about = "経歴" if lang == "jp" else "About"
    nav_research = "研究" if lang == "jp" else "Research"
    nav_pubs = "業績" if lang == "jp" else "Publications"
    nav_contact = "連絡先" if lang == "jp" else "Contact"

    home_file = "index_jp.html" if lang == "jp" else "index.html"
    about_file = "about_jp.html" if lang == "jp" else "about.html"
    research_file = "research_jp.html" if lang == "jp" else "research.html"
    pubs_file = "publications_jp.html" if lang == "jp" else "publications.html"
    contact_file = "contact_jp.html" if lang == "jp" else "contact.html"

    html_content = f"""<!DOCTYPE html>
<html lang="{lang_attr}">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{col_data['title']} — Kosuke Yoshida</title>
    <meta name="description" content="{col_data['summary']}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
</head>

<body class="page-body">
    <div class="background-canvas" id="canvas-container"></div>
    <nav class="glass-nav">
        <div class="nav-content">
            <ul class="nav-links">
                <li><a href="{home_file}">{nav_home}</a></li>
                <li><a href="{about_file}">{nav_about}</a></li>
                <li><a href="{research_file}" class="active">{nav_research}</a></li>
                <li><a href="{pubs_file}">{nav_pubs}</a></li>
                <li><a href="{contact_file}">{nav_contact}</a></li>
            </ul>
            <div class="lang-switch-container">
                <a href="{switch_href}" class="lang-switch-btn" title="{switch_title}">{switch_label}</a>
            </div>
        </div>
    </nav>

    <main class="page-shell">
        <section class="page-hero">
            <div class="container">
                <a class="concept-link back-home" href="{back_href}">{back_label}</a>
                <span class="column-meta-badge">{col_data['tag']} • {col_data['date']}</span>
                <h1 class="column-article-title">{col_data['title']}</h1>
            </div>
        </section>

        <section>
            <div class="container">
                <article class="card glass-card page-card column-article-body fade-in-observe">
{body_html}

                    <div class="column-footer-nav">
                        <a href="{back_href}" class="concept-link">{return_label}</a>
                    </div>
                </article>
            </div>
        </section>
    </main>

    <script src="script.js"></script>
</body>

</html>
"""
    write_text(target_html, html_content)
    print(f"[{target_html.name}] Successfully generated column article HTML")


def main():
    print("--- MyHP Website Content Builder ---")
    update_news(ROOT_DIR / "index.html", CONTENT_DIR / "news_en.txt")
    update_news(ROOT_DIR / "index_jp.html", CONTENT_DIR / "news_jp.txt")
    update_blue_horse(ROOT_DIR / "index.html", CONTENT_DIR / "why_blue_horse_en.txt")
    update_blue_horse(ROOT_DIR / "index_jp.html", CONTENT_DIR / "why_blue_horse_jp.txt")
    update_list_section(ROOT_DIR / "about.html", CONTENT_DIR / "awards_en.txt", "Awards")
    update_list_section(ROOT_DIR / "about_jp.html", CONTENT_DIR / "awards_jp.txt", "受賞 (Awards)")
    update_list_section(ROOT_DIR / "about.html", CONTENT_DIR / "grants_en.txt", "Grants")
    update_list_section(ROOT_DIR / "about_jp.html", CONTENT_DIR / "grants_jp.txt", "助成金・奨学金 (Grants)")
    process_columns()
    print("--- Content build completed successfully! ---")


if __name__ == "__main__":
    main()
