# German Word Notifier

Local-first Python MVP for macOS that shows native notifications with a German word, its translation, and a short definition.

## What it does

The app:

- stores words in a local SQLite database
- imports words from CSV
- picks the next word with a simple least-shown selector
- sends one native macOS notification at a time

The starter CSV currently contains `100` words in [data/words.csv](/Users/darkcreation/Documents/german-word-notifier/data/words.csv).

## Requirements

- macOS
- Python 3.11+

## Setup

```bash
cd /Users/darkcreation/Documents/german-word-notifier
python3 -m venv .venv
source .venv/bin/activate
cp .env.example .env
```

## Where notifications appear

Notifications do not appear inside the terminal or inside VS Code.

They appear in macOS:

- as a banner in the top-right corner
- in Notification Center if you miss the banner

If you do not see them:

1. Open `System Settings` -> `Notifications`.
2. Find the app that runs the command, for example `Terminal` or `iTerm`.
3. Enable notifications for that app.
4. Set the style to `Banners` or `Alerts`.

Important:

- if you run `./gwn` from Terminal, Terminal must be allowed to send notifications
- if you run it from another shell app, that app needs permission instead
- notifications are sent with `osascript`
- clicking the notification may open Script Editor-related UI because macOS treats the sender as AppleScript

## First run

```bash
cd /Users/darkcreation/Documents/german-word-notifier
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

Prints words currently stored in the database, including translation, how many times each word was shown, and when it was last shown.

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

This is the safest way to verify the selector and message formatting.

`./gwn run-once`

Selects the next word from the database and sends a real macOS notification.

`./gwn show-notification --word Haus --translation house --definition "A building for people to live in."`

Sends a manual test notification without using the database selector.

`./gwn show-notification --word Haus --translation house --definition "A building for people to live in." --example "Das Haus ist alt."`

Same as above, but also includes one example sentence.

## Useful examples

Preview the next notification:

```bash
./gwn run-once --dry-run
```

Send a manual test notification:

```bash
./gwn show-notification --word Haus --translation house --definition "A building for people to live in." --example "Das Haus ist alt."
```

Inspect current state:

```bash
./gwn list-words
./gwn stats
```

## Hourly scheduling with launchd

A ready plist template is included at [launchd/com.darkcreation.gwn.hourly.plist](/Users/darkcreation/Documents/german-word-notifier/launchd/com.darkcreation.gwn.hourly.plist).

Install and load it:

```bash
cp /Users/darkcreation/Documents/german-word-notifier/launchd/com.darkcreation.gwn.hourly.plist ~/Library/LaunchAgents/
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

## Notes

- The app stores data in SQLite in `gwn.db` by default.
- Notifications are sent through `osascript`.
- The current MVP is intentionally local-first and does not require any external API.
