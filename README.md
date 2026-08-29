# Friday Assistant

A personal assistant CLI with schedule tracking, communication, vision, Iron Man helmet mode, habits, shopping, recipes, and pomodoro timer.

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## Usage

```bash
friday --help
```

### Commands

| Command | Description |
|---------|-------------|
| `task --add TITLE [--priority high|medium|low]` | Add a task with priority |
| `task --list` | List pending tasks |
| `task --done ID` | Mark task complete |
| `note --add CONTENT [--tags tag1,tag2]` | Add a note with tags |
| `note --list` | List recent notes |
| `event --add TITLE --start DATETIME` | Add schedule event |
| `event --list` | List upcoming events |
| `contact --add NAME --phone PHONE` | Add contact |
| `contact --find NAME` | Find contact |
| `today` | Show today's schedule |
| `steps --count N` | Record daily steps |
| `appointment --book SERVICE` | Book appointment |
| `communicate --sms|--whatsapp|--call PHONE` | Send message or call |
| `tv --device NAME --command CMD` | Send IR command |
| `search QUERY` | Search across data |
| `stats` | Show statistics |
| `remind --add TITLE` | Add reminder |
| `expense --add AMOUNT` | Log expense |
| `export` | Export data to JSON |
| `open google|youtube|instagram|snapchat` | Open website |
| `speak TEXT` | Text to speech |
| `translate TEXT --to LANG` | Translate text |
| `vision IMAGE_PATH` | Analyze image |
| `ask QUESTION` | Answer question |
| `design TEXT --style box|star` | Generate ASCII design |
| `helmet` | Iron Man helmet mode |
| `weather [CITY]` | Get current weather |
| `config --set KEY=VALUE [--file PATH]` | Set config value |
| `config --get KEY [--file PATH]` | Get config value |
| `backup` | Backup database to friday_backup.db |
| `restore [--file PATH]` | Restore database from backup |
| `tv --device NAME --command CMD [--listen]` | Send IR command or listen for voice command |
| `voice --command TEXT` | Speak text aloud |
| `habit --add NAME` | Add a habit |
| `habit --complete ID` | Mark habit complete |
| `habit --list` | List habits with streaks |
| `shopping --add ITEM` | Add shopping item |
| `shopping --toggle ID` | Toggle item bought |
| `shopping --list` | List shopping items |
| `recipe --add NAME` | Add recipe |
| `recipe --list` | List recipes |
| `pomodoro --start [TASK]` | Start pomodoro session |
| `pomodoro --stop ID` | Stop pomodoro session |
| `pomodoro --list` | List pomodoro sessions |

## Notes

- `communicate`, `tv`, and Termux-dependent features print fallback messages if the required commands are unavailable.
- `speak`, `translate`, `vision`, and `ask` degrade gracefully if optional libraries are missing.
- The default user phone number is configured in the package.
- `weather` requires the `OPENWEATHER_API_KEY` env var.
- `config` stores values in `friday.ini` by default.
- `backup` copies `friday.db` to `friday_backup.db`. `restore` replaces `friday.db` with the backup.
- `habit`, `shopping`, `recipe`, and `pomodoro` commands store data in SQLite with foreign keys.
- `pomodoro` tracks focus sessions with start/stop timestamps.
- `tv --listen` uses SpeechRecognition + Google Speech-to-Text to match voice commands.

## 24/7 Operation

### Web Dashboard (Always On)

```bash
python3 web_dashboard/daemon.py
```

Then open `http://localhost:8080` in any browser. The daemon auto-restarts the dashboard if it crashes.

### Production systemd Service

```bash
sudo cp systemd/friday-assistant.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now friday-assistant
sudo journalctl -u friday-assistant -f
```

Logs are written to `web_dashboard/logs/friday_daemon.log`.

### Alternative: Vercel / Render

- `vercel.json` routes requests to `api/app.py`.
- `render.yaml` serves the static dashboard from `web_dashboard/static`.
