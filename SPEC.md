# German Word Notifier for macOS

## Table of Contents

- [Goal](#goal)
- [Product Scope](#product-scope)
- [User Story](#user-story)
- [Core Product Decisions](#core-product-decisions)
- [Functional Requirements](#functional-requirements)
- [Non-Functional Requirements](#non-functional-requirements)
- [Proposed Architecture](#proposed-architecture)
- [Data Model](#data-model)
- [Notification Design](#notification-design)
- [Scheduler Design](#scheduler-design)
- [External Interface Specification](#external-interface-specification)
- [Error Handling](#error-handling)
- [Security and Privacy](#security-and-privacy)
- [Testing Strategy](#testing-strategy)
- [MVP Milestones](#mvp-milestones)
- [Recommended MVP Decision](#recommended-mvp-decision)
- [Implementation Decisions](#implementation-decisions)
- [First Build Plan](#first-build-plan)

## Goal

Build a small Python application for macOS that shows native notifications several times per day with:

- a German word
- translation
- short explanation / gloss
- optional example sentence

The solution should be free to use, simple to run locally on a MacBook, and not depend on paid APIs.

## Product Scope

### In scope

- Local Python application
- Native macOS notifications
- Local storage and caching
- Scheduled delivery several times per day
- Import words from public free sources
- Fetch or enrich definitions from public dictionary-style APIs
- Track which words were already shown
- Basic CLI for setup, import, notify, and debugging

### Out of scope for MVP

- Mobile app
- GUI desktop app
- User accounts or sync
- Complex spaced repetition algorithm
- Audio playback
- Advanced analytics
- Paid APIs

## User Story

As a learner of German on macOS, I want to receive short native notifications with a German word, its translation, and a simple explanation several times per day so I can build vocabulary with low friction.

## Core Product Decisions

### Platform

- Primary platform: macOS
- Runtime: Python 3.11+
- Notification transport: `osascript` via AppleScript

Rationale:

- native on macOS
- no paid dependency
- no extra app required

### Data strategy

Do not depend on a single live dictionary API for the whole product.

Instead split data sources into:

1. local source list of candidate German words
2. remote enrichment for definitions / translations / examples
3. local cache to avoid repeated network calls

### Recommended public sources

#### Source A: primary word and definition source

- `WiktApi` for lookup-style enrichment when a word needs metadata

Use for:

- part of speech
- short definitions
- translations when available
- pronunciation metadata if useful later

#### Source B: example sentences

- `Tatoeba API`

Use for:

- one short example sentence in German
- optional translated example if available

#### Source C: initial word corpus

Use one of:

- frequency list import
- Wiktionary-derived dump
- curated CSV checked into the project later

MVP recommendation:

- start with a local CSV file so the app remains deterministic and easy to test
- later add importer scripts for public datasets

## Functional Requirements

### FR1: Local word repository

The app must maintain a local store of words with at least:

- `word`
- `translation`
- `short_definition`
- `part_of_speech`
- `example_de`
- `example_translation`
- `source`
- `tags`
- `difficulty`
- `times_shown`
- `last_shown_at`
- `created_at`
- `updated_at`
- `is_active`

### FR2: Import words from file

The app must support importing words from a local CSV or JSON file.

Initial required columns:

- `word`
- `translation`
- `short_definition`

Optional columns:

- `part_of_speech`
- `example_de`
- `example_translation`
- `tags`
- `difficulty`

### FR3: Enrich incomplete entries

If a local word is missing translation, definition, or example, the app should be able to enrich it from public APIs and cache the result locally.

### FR4: Notification delivery

The app must show a native macOS notification containing:

- title: German word
- subtitle: translation
- body: short definition and optionally example

Example:

- Title: `Haus`
- Subtitle: `house`
- Body: `A building for people to live in. Example: Das Haus ist alt.`

### FR5: Scheduling

The system must support multiple deliveries per day.

MVP scheduling options:

1. `launchd` with multiple daily triggers
2. cron-like external trigger that runs the CLI

Preferred option:

- `launchd`, because it is native on macOS and reliable for user sessions

### FR6: Word selection

The app must select a word to show based on simple rules:

- prefer words shown less often
- avoid showing the same word twice in a short window
- allow optional tag filtering

MVP selection rule:

- pick an active word with the lowest `times_shown`
- among ties, prefer older `last_shown_at`
- randomize among the remaining candidates

### FR7: CLI commands

The app must expose a CLI with commands similar to:

- `init-db`
- `import-csv`
- `enrich-word`
- `enrich-missing`
- `show-notification`
- `run-once`
- `list-words`
- `stats`

### FR8: Configuration

The app must load configuration from:

1. `.env`
2. environment variables
3. sensible defaults

Configurable values:

- database path
- source file path
- notification schedule assumptions
- default language for translation output
- max body length
- example enabled true/false
- API timeout
- API rate limit pause

## Non-Functional Requirements

### NFR1: Cost

- The MVP must be usable for free.

### NFR2: Simplicity

- The MVP must be runnable by one user on one Mac with minimal setup.

### NFR3: Reliability

- If remote APIs fail, the app must still work with cached or pre-imported local data.

### NFR4: Performance

- A normal notification run should complete in under 2 seconds when data is already cached.

### NFR5: Observability

- The app must log key events for imports, enrichment, scheduling runs, and failures.

## Proposed Architecture

### Project layout

```text
german-word-notifier/
  SPEC.md
  README.md
  pyproject.toml
  .env.example
  data/
    words.csv
  src/
    app/
      __init__.py
      cli.py
      config.py
      db.py
      models.py
      selector.py
      notifier.py
      scheduler.py
      services/
        dictionary.py
        examples.py
        importer.py
  tests/
    test_selector.py
    test_importer.py
    test_notifier.py
```

### Components

#### `config.py`

- loads environment
- validates paths and defaults

#### `db.py`

- SQLite connection handling
- schema creation
- common queries

#### `models.py`

- typed models or dataclasses for word records

#### `services/importer.py`

- imports CSV / JSON into the local database

#### `services/dictionary.py`

- fetches and normalizes dictionary metadata from public API

#### `services/examples.py`

- fetches and normalizes example sentences

#### `selector.py`

- chooses the next word to display

#### `notifier.py`

- builds notification text
- calls `osascript`

#### `cli.py`

- exposes commands for manual and scheduled execution

## Data Model

### Table: `words`

Suggested schema:

```sql
CREATE TABLE words (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  word TEXT NOT NULL UNIQUE,
  translation TEXT,
  short_definition TEXT,
  part_of_speech TEXT,
  example_de TEXT,
  example_translation TEXT,
  source TEXT,
  tags TEXT,
  difficulty INTEGER,
  times_shown INTEGER NOT NULL DEFAULT 0,
  last_shown_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  is_active INTEGER NOT NULL DEFAULT 1
);
```

### Table: `notification_log`

```sql
CREATE TABLE notification_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  word_id INTEGER NOT NULL,
  shown_at TEXT NOT NULL,
  status TEXT NOT NULL,
  message TEXT,
  FOREIGN KEY (word_id) REFERENCES words(id)
);
```

## Notification Design

### Notification fields

- title: German word
- subtitle: translation or part of speech
- body: short definition plus one optional example sentence

### Body length limits

MVP guideline:

- hard truncate to roughly 180 to 220 characters for readability

### Fallback rendering

If data is partial:

- title = word
- subtitle = translation if available, else `German word`
- body = definition if available, else `Open app/CLI for details`

## Scheduler Design

### Preferred implementation

Use `launchd` to trigger the CLI command multiple times per day.

Example execution flow:

1. `launchd` starts `python -m app.cli run-once`
2. app selects one word
3. app shows notification
4. app updates counters and logs the result

### Example daily cadence

- 09:00
- 12:30
- 16:00
- 20:30

This schedule should be configurable.

## External Interface Specification

### CLI examples

```bash
python -m app.cli init-db
python -m app.cli import-csv data/words.csv
python -m app.cli enrich-missing --limit 50
python -m app.cli run-once
python -m app.cli stats
```

### Dictionary service contract

Input:

- `word: str`

Output normalized payload:

```json
{
  "word": "Haus",
  "translation": "house",
  "short_definition": "A building for people to live in.",
  "part_of_speech": "noun",
  "example_de": "Das Haus ist alt.",
  "example_translation": "The house is old.",
  "source": "wiktapi+tatoeba"
}
```

## Error Handling

### Dictionary API failure

- log the failure
- do not fail the whole app if local data exists
- mark enrichment attempt as failed

### Notification failure

- capture stderr / AppleScript error text
- write failure to `notification_log`
- do not corrupt `times_shown`

### Empty database

- return a clear CLI error:
  `No active words available. Import or enrich data first.`

## Security and Privacy

- No user account required
- All learned data stored locally
- API calls should send only the word being queried
- No analytics in MVP

## Testing Strategy

### Unit tests

- selector behavior
- CSV import validation
- notification text formatting
- API response normalization

### Integration tests

- import sample CSV into SQLite
- run one enrichment cycle with mocked HTTP responses
- run one notification cycle with mocked notifier shell call

### Manual test checklist

- database initializes
- CSV imports cleanly
- one notification appears on macOS
- repeated runs rotate across words
- missing network still allows cached notifications

## MVP Milestones

### Milestone 1: local-only prototype

- create SQLite schema
- import CSV
- select next word
- show macOS notification

Exit criterion:

- local CSV with 20+ words can drive notifications without network access

### Milestone 2: enrichment layer

- add dictionary service
- add example sentence service
- cache responses into SQLite

Exit criterion:

- app can enrich partial records automatically

### Milestone 3: scheduling

- add `launchd` plist template
- document installation and schedule updates

Exit criterion:

- notifications arrive automatically several times per day

### Milestone 4: quality pass

- tests
- logging cleanup
- config cleanup
- README setup instructions

## Recommended MVP Decision

To keep implementation small and reliable, build the first working version around this flow:

1. import a local CSV of German words
2. store everything in SQLite
3. show native macOS notifications via `osascript`
4. schedule runs with `launchd`
5. add optional API enrichment only after the local flow works

This avoids the main risk: depending on unstable or rate-limited public APIs before the basic product works.

## Implementation Decisions

- Translation target language for MVP: English only
- Example sentence policy for MVP: show at most one example sentence
- Selection strategy for v1: simple least-shown rotation
- Source word list policy: import from user-provided files only

## First Build Plan

Implementation should start with:

1. `pyproject.toml`
2. SQLite schema and CLI skeleton
3. CSV importer
4. `osascript` notification sender
5. `run-once` command
6. sample `data/words.csv`

Only after that:

7. dictionary API client
8. example sentence API client
9. `launchd` plist template
10. tests and docs
