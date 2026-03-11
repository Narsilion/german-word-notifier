# German Word Notifier

Local-first Python MVP for macOS that shows native notifications with a German word, its article when available, and its English translation, and can open a local study page when you click the notification.

## What it does

The app:

- stores words in a local SQLite database
- imports words from CSV
- picks the next word with a simple least-shown selector
- sends one native macOS notification at a time

The starter CSV currently contains `105` words in [data/words.csv](/Users/darkcreation/Documents/git_repos/german-word-notifier/data/words.csv).

## Requirements

- macOS
- Python 3.11+

## Setup

```bash
cd /Users/darkcreation/Documents/git_repos/german-word-notifier
python3 -m venv .venv
source .venv/bin/activate
cp .env.example .env
```

## Where notifications appear

Notifications do not appear inside the terminal or inside VS Code.

They appear in macOS:

- as a banner in the top-right corner
- in Notification Center if you miss the banner
- clicking the notification or the `Open Card` action opens a generated HTML study page for that word
- the generated study page includes pronunciation buttons for the word and the German example sentence when supported by the browser

If you do not see them:

1. Open `System Settings` -> `Notifications`.
2. Find the app that runs the command, for example `Terminal` or `iTerm`.
3. Enable notifications for that app.
4. Set the style to `Banners` or `Alerts`.

Important:

- if you run `./gwn` from Terminal, Terminal must be allowed to send notifications
- if you run it from another shell app, that app needs permission instead
- notifications are sent with `terminal-notifier` when available so clicks can open the study page
- if `terminal-notifier` is unavailable, the app falls back to the built-in notification path
- the generated HTML pages are stored in `.generated-pages/` by default

## First run

```bash
cd /Users/darkcreation/Documents/git_repos/german-word-notifier
./gwn init-db
./gwn import-csv data/words.csv
./gwn run-once --dry-run
./gwn run-once
```

What happens:

- `run-once --dry-run` prints the notification content without sending it
- `run-once` sends a real macOS notification

## Commands

`./gwn init-db`

Creates the SQLite database and required tables.

`./gwn import-csv <path>`

Imports words from a CSV file into the local database. If `<path>` is omitted, the app uses the default file from `.env` or `data/words.csv`.

`./gwn list-words`

Prints words currently stored in the database, including the article when available, translation, how many times each word was shown, and when it was last shown.

`./gwn list-words --limit 50`

Same as `list-words`, but shows more rows.

`./gwn stats`

Shows database and notification counters:

- total words
- active words
- shown words
- sent notifications
- failed notifications

`./gwn run-once --dry-run`

Selects the next word and prints the generated notification payload:

- title
- subtitle
- body
- page path

This is the safest way to verify the selector and message formatting. The notification shows the English translation and, when available, the German example sentence in the body.

`./gwn run-once`

Selects the next word from the database and sends a real macOS notification.

`./gwn show-notification --word Haus --article das --translation house`

Sends a manual test notification without using the database selector.

`./gwn show-notification --word Haus --article das --translation house --definition "A building for people to live in." --example "Das Haus ist alt."`

Extra definition values may still be stored, but they are no longer shown. The German example sentence is still shown in the notification and generated study page when available.

## Useful examples

Preview the next notification:

```bash
./gwn run-once --dry-run
```

Open the generated HTML card directly:

```bash
open .generated-pages/das-haus.html
```

Inside the page, click `Pronounce` to hear the word or `Pronounce Example` to hear the German example sentence with the browser's available German voice.

Send a manual test notification:

```bash
./gwn show-notification --word Haus --article das --translation house
```

Inspect current state:

```bash
./gwn list-words
./gwn stats
```

## Hourly scheduling with launchd

A ready plist template is included at [launchd/com.darkcreation.gwn.hourly.plist](/Users/darkcreation/Documents/git_repos/german-word-notifier/launchd/com.darkcreation.gwn.hourly.plist).

Install and load it:

```bash
cp /Users/darkcreation/Documents/git_repos/german-word-notifier/launchd/com.darkcreation.gwn.hourly.plist ~/Library/LaunchAgents/
launchctl unload ~/Library/LaunchAgents/com.darkcreation.gwn.hourly.plist 2>/dev/null
launchctl load ~/Library/LaunchAgents/com.darkcreation.gwn.hourly.plist
launchctl start com.darkcreation.gwn.hourly
```

What it does:

- runs `python3 -m app.cli run-once`
- triggers every `3600` seconds
- also runs once immediately after loading because `RunAtLoad` is enabled

Useful checks:

```bash
launchctl list | grep gwn
tail -f /tmp/gwn.stdout.log
tail -f /tmp/gwn.stderr.log
```

The scheduler logs now include UTC timestamps and event markers such as `RUN_START`, `RUN_SENT`, and `RUN_FAILED`, plus the notification backend used, so you can verify exactly when each scheduled run executed.

## Notes

- The app stores data in SQLite in `gwn.db` by default.
- Notification detail pages are generated locally in `.generated-pages` by default.
- The current MVP is intentionally local-first and does not require any external API.
