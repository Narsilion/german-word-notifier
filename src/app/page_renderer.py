from __future__ import annotations

from html import escape
from pathlib import Path

from app.models import WordRecord


def write_word_page(output_dir: Path, word: WordRecord) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    page_path = output_dir / f"{_slugify(word.display_word)}.html"
    page_path.write_text(_build_html(word), encoding="utf-8")
    return page_path


def _build_html(word: WordRecord) -> str:
    chips: list[str] = []
    if word.part_of_speech:
        chips.append(_chip(word.part_of_speech))
    if word.translation:
        chips.append(_chip(word.translation))
    if word.tags:
        chips.append(_chip(word.tags))

    example_block = ""
    if word.example_de or word.example_translation:
        lines: list[str] = []
        if word.example_de:
            lines.append(f"<p class=\"example-de\">{escape(word.example_de)}</p>")
        if word.example_translation:
            lines.append(f"<p class=\"example-en\">{escape(word.example_translation)}</p>")
        example_block = f"""
        <section class="panel example-panel">
          <h2>Example</h2>
          {''.join(lines)}
        </section>
        """

    definition = escape(word.short_definition or "No definition available.")
    article = escape(word.article.upper()) if word.article else "WORD"
    translation = escape(word.translation or "Translation unavailable")
    display_word = escape(word.display_word)

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{display_word}</title>
    <style>
      :root {{
        --bg-top: #f2e8d7;
        --bg-bottom: #d8e5ec;
        --ink: #18222f;
        --muted: #52606f;
        --panel: rgba(255, 252, 246, 0.88);
        --accent: #bb5a34;
        --accent-soft: #e7b89f;
        --ring: rgba(24, 34, 47, 0.08);
        --shadow: 0 28px 80px rgba(24, 34, 47, 0.18);
      }}

      * {{
        box-sizing: border-box;
      }}

      body {{
        margin: 0;
        min-height: 100vh;
        font-family: "Avenir Next", "Helvetica Neue", sans-serif;
        color: var(--ink);
        background:
          radial-gradient(circle at top left, rgba(255,255,255,0.78), transparent 32%),
          radial-gradient(circle at bottom right, rgba(187,90,52,0.16), transparent 28%),
          linear-gradient(160deg, var(--bg-top), var(--bg-bottom));
      }}

      .shell {{
        width: min(920px, calc(100vw - 32px));
        margin: 32px auto;
        padding: 28px;
        border: 1px solid var(--ring);
        border-radius: 28px;
        background: var(--panel);
        box-shadow: var(--shadow);
        backdrop-filter: blur(14px);
      }}

      .hero {{
        position: relative;
        overflow: hidden;
        padding: 28px;
        border-radius: 24px;
        background:
          linear-gradient(135deg, rgba(24,34,47,0.95), rgba(36,59,77,0.88)),
          linear-gradient(135deg, rgba(187,90,52,0.5), rgba(231,184,159,0.16));
        color: #f8f4ee;
      }}

      .hero::after {{
        content: "";
        position: absolute;
        inset: auto -8% -26% auto;
        width: 260px;
        height: 260px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(231,184,159,0.3), transparent 68%);
      }}

      .label {{
        display: inline-flex;
        align-items: center;
        padding: 6px 12px;
        border-radius: 999px;
        background: rgba(255,255,255,0.12);
        letter-spacing: 0.22em;
        font-size: 12px;
        text-transform: uppercase;
      }}

      h1 {{
        margin: 18px 0 6px;
        font-family: "Palatino", "Book Antiqua", serif;
        font-size: clamp(42px, 8vw, 72px);
        line-height: 0.95;
      }}

      .translation {{
        margin: 0;
        font-size: clamp(20px, 3vw, 30px);
        color: rgba(248,244,238,0.84);
      }}

      .definition {{
        margin: 18px 0 0;
        max-width: 44rem;
        font-size: 18px;
        line-height: 1.6;
        color: rgba(248,244,238,0.92);
      }}

      .chips {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 22px 0 0;
      }}

      .chip {{
        padding: 8px 12px;
        border-radius: 999px;
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.14);
        font-size: 14px;
      }}

      .grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 18px;
        margin-top: 18px;
      }}

      .panel {{
        padding: 22px;
        border-radius: 22px;
        background: rgba(255,255,255,0.72);
        border: 1px solid rgba(24,34,47,0.08);
      }}

      .panel h2 {{
        margin: 0 0 12px;
        font-size: 14px;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--muted);
      }}

      .panel p {{
        margin: 0;
        font-size: 18px;
        line-height: 1.6;
      }}

      .example-panel {{
        margin-top: 18px;
        background:
          linear-gradient(135deg, rgba(255,255,255,0.88), rgba(231,184,159,0.26));
      }}

      .example-de {{
        font-family: "Palatino", "Book Antiqua", serif;
        font-size: 28px;
      }}

      .example-en {{
        margin-top: 12px !important;
        color: var(--muted);
      }}

      .footer {{
        display: flex;
        justify-content: space-between;
        gap: 16px;
        margin-top: 18px;
        color: var(--muted);
        font-size: 14px;
      }}

      @media (max-width: 640px) {{
        .shell {{
          margin: 16px auto;
          padding: 16px;
        }}

        .hero {{
          padding: 22px;
        }}

        .footer {{
          flex-direction: column;
        }}
      }}
    </style>
  </head>
  <body>
    <main class="shell">
      <section class="hero">
        <span class="label">{article}</span>
        <h1>{display_word}</h1>
        <p class="translation">{translation}</p>
        <p class="definition">{definition}</p>
        <div class="chips">
          {''.join(chips)}
        </div>
      </section>

      <section class="grid">
        <article class="panel">
          <h2>German</h2>
          <p>{display_word}</p>
        </article>
        <article class="panel">
          <h2>Meaning</h2>
          <p>{translation}</p>
        </article>
      </section>

      {example_block}

      <div class="footer">
        <span>Generated by German Word Notifier</span>
        <span>Keep the article attached to the noun when you review it.</span>
      </div>
    </main>
  </body>
</html>
"""


def _chip(value: str) -> str:
    return f"<span class=\"chip\">{escape(value)}</span>"


def _slugify(value: str) -> str:
    characters = []
    for char in value.lower():
        if char.isalnum():
            characters.append(char)
        elif char in {" ", "-", "_"}:
            characters.append("-")
    slug = "".join(characters).strip("-")
    return slug or "word"
