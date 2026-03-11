from __future__ import annotations

import json
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
    if word.example_de:
        example_block = f"""
      <section class="panel example-panel">
        <div class="panel-header">
          <h2>Example</h2>
          <button class="pronounce-button pronounce-button-inline" id="pronounce-example-button" type="button">
            Pronounce Example
          </button>
        </div>
        <p class="example-de">{escape(word.example_de)}</p>
      </section>
        """
    article = escape(word.article.upper()) if word.article else "WORD"
    translation = escape(word.translation or "Translation unavailable")
    display_word = escape(word.display_word)
    pronunciation_word = json.dumps(word.word)
    pronunciation_example = json.dumps(word.example_de or "")

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

      .hero-actions {{
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 12px;
        margin-top: 18px;
      }}

      .pronounce-button {{
        appearance: none;
        border: 0;
        border-radius: 999px;
        padding: 12px 18px;
        font: inherit;
        font-weight: 600;
        color: #18222f;
        background: linear-gradient(135deg, #f8e7c6, #ffffff);
        box-shadow: 0 10px 24px rgba(24, 34, 47, 0.18);
        cursor: pointer;
      }}

      .pronounce-button:hover {{
        transform: translateY(-1px);
      }}

      .pronounce-button:disabled {{
        cursor: not-allowed;
        opacity: 0.65;
        transform: none;
      }}

      .pronounce-status {{
        min-height: 1.5em;
        font-size: 14px;
        color: rgba(248,244,238,0.84);
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

      .panel-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
      }}

      .panel-header h2 {{
        margin: 0;
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

      .pronounce-button-inline {{
        padding: 8px 14px;
        box-shadow: none;
        background: rgba(24, 34, 47, 0.08);
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

        .panel-header {{
          align-items: flex-start;
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
        <div class="hero-actions">
          <button class="pronounce-button" id="pronounce-button" type="button">Pronounce</button>
          <span class="pronounce-status" id="pronounce-status" aria-live="polite"></span>
        </div>
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
    <script>
      (() => {{
        const button = document.getElementById("pronounce-button");
        const exampleButton = document.getElementById("pronounce-example-button");
        const status = document.getElementById("pronounce-status");
        const wordText = {pronunciation_word};
        const exampleText = {pronunciation_example};

        if (!("speechSynthesis" in window) || typeof SpeechSynthesisUtterance === "undefined") {{
          button.disabled = true;
          if (exampleButton) {{
            exampleButton.disabled = true;
          }}
          status.textContent = "Pronunciation is not supported in this browser.";
          return;
        }}

        const speech = window.speechSynthesis;

        const chooseVoice = () => {{
          const voices = speech.getVoices();
          return voices.find((voice) => voice.lang === "de-DE")
            || voices.find((voice) => voice.lang.toLowerCase().startsWith("de"))
            || null;
        }};

        const speak = (text, label) => {{
          if (!text) {{
            status.textContent = `${{label}} is unavailable.`;
            return;
          }}
          speech.cancel();
          const utterance = new SpeechSynthesisUtterance(text);
          utterance.lang = "de-DE";
          utterance.rate = 0.9;

          const voice = chooseVoice();
          if (voice) {{
            utterance.voice = voice;
            status.textContent = `Voice: ${{voice.name}}`;
          }} else {{
            status.textContent = "Using browser default voice.";
          }}

          utterance.onend = () => {{
            status.textContent = "";
          }};
          utterance.onerror = () => {{
            status.textContent = "Pronunciation failed.";
          }};

          speech.speak(utterance);
        }};

        button.addEventListener("click", () => speak(wordText, "Word pronunciation"));
        if (exampleButton) {{
          exampleButton.addEventListener("click", () => speak(exampleText, "Example pronunciation"));
        }}

        if (typeof speech.onvoiceschanged !== "undefined") {{
          speech.onvoiceschanged = () => {{
            chooseVoice();
          }};
        }}
      }})();
    </script>
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
