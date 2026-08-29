# Friday Assistant

A personal assistant CLI with schedule tracking, communication, vision, and Iron Man helmet mode.

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
| `task --add TITLE` | Add a task |
| `task --list` | List pending tasks |
| `task --done ID` | Mark task complete |
| `note --add CONTENT` | Add a note |
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

## Notes

- `communicate`, `tv`, and Termux-dependent features print fallback messages if the required commands are unavailable.
- `speak`, `translate`, `vision`, and `ask` degrade gracefully if optional libraries are missing.
- The default user phone number is configured in the package.
