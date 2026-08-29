import argparse
import json
import sys
from datetime import datetime
from typing import Optional

from friday_assistant.db import (
    connect_db,
    get_user_id,
    setup_database,
)
from friday_assistant.models import (
    add_schedule_event,
    add_task,
    complete_task,
    add_note,
    add_contact,
    find_contact,
    add_appointment,
    log_action,
    queue_tv_command,
    add_reminder,
    add_expense,
    record_steps,
    get_tasks,
    get_upcoming_events,
    get_today_events,
    get_notes,
    search_all,
    get_stats,
    export_data,
    add_habit,
    complete_habit,
    get_habits,
    add_shopping_item,
    toggle_shopping_item,
    get_shopping_items,
    add_recipe,
    add_recipe_ingredient,
    get_recipes,
    get_recipe_ingredients,
    start_pomodoro,
    end_pomodoro,
    get_pomodoro_sessions,
)
from friday_assistant.comm import send_sms, send_whatsapp, make_call, ir_send
from friday_assistant.utils import (
    open_url,
    speak_text,
    translate_text,
    analyze_image,
    answer_question,
    helmet_mode,
    design_ascii,
    get_weather,
    load_config,
    save_config,
    backup_db,
    restore_db,
    listen_command,
    match_tv_command,
)


MY_PHONE = "6043282162"


def build_parser(argv: Optional[list] = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Friday personal assistant CLI")
    subparsers = parser.add_subparsers(dest="command")

    task_parser = subparsers.add_parser("task", help="Manage tasks")
    task_parser.add_argument("--add", metavar="TITLE", help="Add a new task")
    task_parser.add_argument("--done", metavar="ID", type=int, help="Mark task as complete")
    task_parser.add_argument("--list", action="store_true", help="List pending tasks")
    task_parser.add_argument("--priority", metavar="PRI", default="medium", choices=["high", "medium", "low"], help="Task priority")

    note_parser = subparsers.add_parser("note", help="Manage notes")
    note_parser.add_argument("--add", metavar="CONTENT", help="Add a note")
    note_parser.add_argument("--list", action="store_true", help="List recent notes")
    note_parser.add_argument("--tags", metavar="TAGS", help="Comma-separated tags for the note")

    event_parser = subparsers.add_parser("event", help="Manage schedule events")
    event_parser.add_argument("--add", metavar="TITLE", help="Add a schedule event")
    event_parser.add_argument("--start", metavar="DATETIME", help="Event start time (ISO format)")
    event_parser.add_argument("--end", metavar="DATETIME", help="Event end time (ISO format)")
    event_parser.add_argument("--location", metavar="LOC", help="Event location")
    event_parser.add_argument("--details", metavar="TEXT", help="Event details")
    event_parser.add_argument("--list", action="store_true", help="List upcoming events")

    contact_parser = subparsers.add_parser("contact", help="Manage contacts")
    contact_parser.add_argument("--add", metavar="NAME", help="Add a contact")
    contact_parser.add_argument("--phone", metavar="PHONE", help="Contact phone")
    contact_parser.add_argument("--email", metavar="EMAIL", help="Contact email")
    contact_parser.add_argument("--find", metavar="NAME", help="Find a contact")

    steps_parser = subparsers.add_parser("steps", help="Record daily steps")
    steps_parser.add_argument("--count", metavar="N", type=int, help="Step count")
    steps_parser.add_argument("--date", metavar="YYYY-MM-DD", help="Date for step record")

    appt_parser = subparsers.add_parser("appointment", help="Manage appointments")
    appt_parser.add_argument("--book", metavar="SERVICE", help="Book an appointment")
    appt_parser.add_argument("--start", metavar="DATETIME", help="Appointment start time")
    appt_parser.add_argument("--provider", metavar="NAME", help="Service provider")

    comm_parser = subparsers.add_parser("communicate", help="Send communications")
    comm_parser.add_argument("--sms", metavar="PHONE", help="Send SMS to phone")
    comm_parser.add_argument("--whatsapp", metavar="PHONE", help="Send WhatsApp to phone")
    comm_parser.add_argument("--call", metavar="PHONE", help="Call phone number")
    comm_parser.add_argument("--message", metavar="TEXT", help="Message content")

    tv_parser = subparsers.add_parser("tv", help="TV remote commands")
    tv_parser.add_argument("--device", metavar="NAME", required=True, help="IR device name")
    tv_parser.add_argument("--command", metavar="CMD", help="IR command to send")
    tv_parser.add_argument("--listen", action="store_true", help="Listen for voice command")

    voice_parser = subparsers.add_parser("voice", help="Voice control")
    voice_parser.add_argument("--device", metavar="NAME", default="Google", help="Wake word")
    voice_parser.add_argument("--command", metavar="CMD", help="Command to speak")

    search_parser = subparsers.add_parser("search", help="Search across tasks, notes, contacts, events")
    search_parser.add_argument("query", metavar="QUERY", help="Search term")

    subparsers.add_parser("stats", help="Show statistics")

    remind_parser = subparsers.add_parser("remind", help="Manage reminders")
    remind_parser.add_argument("--add", metavar="TITLE", help="Add a reminder")
    remind_parser.add_argument("--at", metavar="DATETIME", help="Due time for reminder")

    expense_parser = subparsers.add_parser("expense", help="Manage expenses")
    expense_parser.add_argument("--add", metavar="AMOUNT", type=float, help="Add an expense amount")
    expense_parser.add_argument("--category", metavar="CAT", help="Expense category")
    expense_parser.add_argument("--note", metavar="TEXT", help="Expense note")

    subparsers.add_parser("export", help="Export data to JSON")
    subparsers.add_parser("today", help="Show today's schedule")

    open_parser = subparsers.add_parser("open", help="Open websites")
    open_parser.add_argument("site", choices=["google", "youtube", "instagram", "snapchat"], help="Site to open")

    speak_parser = subparsers.add_parser("speak", help="Text to speech")
    speak_parser.add_argument("text", metavar="TEXT", help="Text to speak")

    translate_parser = subparsers.add_parser("translate", help="Translate text")
    translate_parser.add_argument("text", metavar="TEXT", help="Text to translate")
    translate_parser.add_argument("--to", metavar="LANG", default="en", help="Target language code")

    vision_parser = subparsers.add_parser("vision", help="Analyze image")
    vision_parser.add_argument("image", metavar="IMAGE_PATH", help="Path to image file")

    ask_parser = subparsers.add_parser("ask", help="Answer a question")
    ask_parser.add_argument("question", metavar="QUESTION", help="Question to answer")

    design_parser = subparsers.add_parser("design", help="Generate ASCII design")
    design_parser.add_argument("text", metavar="TEXT", help="Text to design")
    design_parser.add_argument("--style", metavar="STYLE", default="box", choices=["box", "star"], help="Design style")

    subparsers.add_parser("helmet", help="Iron Man helmet mode")

    weather_parser = subparsers.add_parser("weather", help="Get weather")
    weather_parser.add_argument("city", metavar="CITY", nargs="?", default="Vancouver", help="City name")

    config_parser = subparsers.add_parser("config", help="Manage config")
    config_parser.add_argument("--set", metavar="KEY=VALUE", help="Set config value")
    config_parser.add_argument("--get", metavar="KEY", help="Get config value")
    config_parser.add_argument("--file", metavar="PATH", default="friday.ini", help="Config file path")

    subparsers.add_parser("backup", help="Backup database")
    restore_parser = subparsers.add_parser("restore", help="Restore database")
    restore_parser.add_argument("--file", metavar="PATH", default="friday_backup.db", help="Backup file path")

    habit_parser = subparsers.add_parser("habit", help="Manage habits")
    habit_parser.add_argument("--add", metavar="NAME", help="Add a habit")
    habit_parser.add_argument("--complete", metavar="ID", type=int, help="Mark habit complete")
    habit_parser.add_argument("--list", action="store_true", help="List habits")

    shopping_parser = subparsers.add_parser("shopping", help="Shopping list")
    shopping_parser.add_argument("--add", metavar="ITEM", help="Add shopping item")
    shopping_parser.add_argument("--toggle", metavar="ID", type=int, help="Toggle item bought")
    shopping_parser.add_argument("--list", action="store_true", help="List shopping items")

    recipe_parser = subparsers.add_parser("recipe", help="Recipe manager")
    recipe_parser.add_argument("--add", metavar="NAME", help="Add a recipe")
    recipe_parser.add_argument("--ingredient", metavar="NAME", help="Ingredient name")
    recipe_parser.add_argument("--amount", metavar="AMOUNT", help="Ingredient amount")
    recipe_parser.add_argument("--list", action="store_true", help="List recipes")

    pomodoro_parser = subparsers.add_parser("pomodoro", help="Pomodoro timer")
    pomodoro_parser.add_argument("--start", metavar="TASK", nargs="?", help="Start pomodoro session")
    pomodoro_parser.add_argument("--stop", metavar="ID", type=int, help="Stop pomodoro session")
    pomodoro_parser.add_argument("--list", action="store_true", help="List pomodoro sessions")

    return parser.parse_args(argv)


def main(argv: Optional[list] = None) -> int:
    args = build_parser(argv)
    conn = connect_db()
    setup_database(conn)
    user_id = get_user_id(conn, "Default User", "user@example.com", MY_PHONE)

    try:
        if args.command == "task":
            if args.add:
                add_task(conn, user_id, args.add, priority=args.priority)
                print(f"Task added: {args.add} [{args.priority}]")
            elif args.done:
                complete_task(conn, args.done)
                print(f"Task {args.done} marked complete")
            elif args.list:
                tasks = get_tasks(conn, user_id)
                for t in tasks:
                    status = "done" if t[3] else "pending"
                    print(f"[{t[0]}] {t[1]} ({status}) [{t[5]}]")
            else:
                print("Usage: friday task --add TITLE [--priority high|medium|low] | --done ID | --list")
                return 1

        elif args.command == "note":
            if args.add:
                add_note(conn, user_id, args.add, args.tags)
                print("Note added")
            elif args.list:
                notes = get_notes(conn, user_id)
                for n in notes:
                    tags = f" [{n[3]}]" if n[3] else ""
                    print(f"[{n[0]}] {n[1]} ({n[2]}){tags}")
            else:
                print("Usage: friday note --add CONTENT [--tags tag1,tag2] | --list")
                return 1

        elif args.command == "event":
            if args.add:
                add_schedule_event(conn, user_id, args.add, args.start or datetime.now().isoformat(),
                                   args.end, args.location, args.details)
                print(f"Event added: {args.add}")
            elif args.list:
                events = get_upcoming_events(conn, user_id)
                for e in events:
                    print(f"[{e[0]}] {e[1]} at {e[2]} ({e[3] or 'no end'})")
            else:
                print("Usage: friday event --add TITLE --start DATETIME [--end DATETIME] [--location LOC] [--details TEXT] | --list")
                return 1

        elif args.command == "contact":
            if args.add:
                add_contact(conn, args.add, args.phone, args.email)
                print(f"Contact added: {args.add}")
            elif args.find:
                c = find_contact(conn, args.find)
                if c:
                    print(f"[{c[0]}] {c[1]} | Phone: {c[2]} | Email: {c[3]}")
                else:
                    print("Contact not found")
            else:
                print("Usage: friday contact --add NAME [--phone PHONE] [--email EMAIL] | --find NAME")
                return 1

        elif args.command == "steps":
            if args.count is not None:
                record_steps(conn, args.count, args.date)
                print(f"Recorded {args.count} steps")
            else:
                print("Usage: friday steps --count N [--date YYYY-MM-DD]")
                return 1

        elif args.command == "appointment":
            if args.book:
                add_appointment(conn, args.book, args.start or datetime.now().isoformat(), args.provider)
                print(f"Appointment booked: {args.book}")
            else:
                print("Usage: friday appointment --book SERVICE --start DATETIME [--provider NAME]")
                return 1

        elif args.command == "communicate":
            message = args.message or ""
            if args.sms:
                send_sms(args.sms, message)
            elif args.whatsapp:
                send_whatsapp(args.whatsapp, message)
            elif args.call:
                make_call(args.call)
            else:
                print("Usage: friday communicate --sms|--whatsapp PHONE [--message TEXT] | --call PHONE")
                return 1

        elif args.command == "tv":
            if not args.listen and not args.command:
                print("Usage: friday tv --device NAME --command CMD | --listen")
                return 1
            if args.listen:
                transcript = listen_command(args.device)
                if transcript:
                    device, command = match_tv_command(transcript)
                    if device and command:
                        ir_send(args.device, command)
                        print(f"Voice command: {transcript} -> sent '{command}' to {args.device}")
                    else:
                        print(f"Could not match TV command from: {transcript}")
                else:
                    print("No voice command detected.")
            else:
                ir_send(args.device, args.command)
                print(f"Sent IR command to {args.device}: {args.command}")

        elif args.command == "voice":
            if args.command:
                speak_text(args.command)
                print(f"Spoke: {args.command}")
            else:
                print("Usage: friday voice --command TEXT")
                return 1

        elif args.command == "search":
            results = search_all(conn, user_id, args.query)
            for category, items in results.items():
                if items:
                    print(f"\n--- {category.upper()} ---")
                    for item in items:
                        print(item)

        elif args.command == "stats":
            stats = get_stats(conn, user_id)
            print("Friday Stats")
            print(f"Tasks: {stats['tasks_total']} total, {stats['tasks_completed']} completed")
            print(f"Notes: {stats['notes']}")
            print(f"Events: {stats['events']}")
            print(f"Contacts: {stats['contacts']}")
            print(f"Total Steps: {stats['total_steps']}")
            print(f"Total Expenses: ${stats['total_expenses']:.2f}")

        elif args.command == "remind":
            if args.add:
                due = args.at or datetime.now().isoformat()
                add_reminder(conn, user_id, args.add, due)
                print(f"Reminder added: {args.add} at {due}")
            else:
                print("Usage: friday remind --add TITLE [--at DATETIME]")
                return 1

        elif args.command == "expense":
            if args.add is not None:
                add_expense(conn, user_id, args.add, args.category, args.note)
                print(f"Expense added: ${args.add:.2f}")
            else:
                print("Usage: friday expense --add AMOUNT [--category CAT] [--note TEXT]")
                return 1

        elif args.command == "export":
            data = export_data(conn, user_id)
            print(json.dumps(data, indent=2))

        elif args.command == "today":
            events = get_today_events(conn, user_id)
            if events:
                print("Today's Schedule:")
                for e in events:
                    print(f"[{e[0]}] {e[1]} at {e[2]} ({e[3] or 'no end'}) | {e[4] or ''}")
            else:
                print("No events scheduled for today.")

        elif args.command == "open":
            urls = {
                "google": "https://www.google.com",
                "youtube": "https://www.youtube.com",
                "instagram": "https://www.instagram.com",
                "snapchat": "https://www.snapchat.com",
            }
            open_url(urls[args.site])
            print(f"Opening {args.site}...")

        elif args.command == "speak":
            speak_text(args.text)
            print(f"Speaking: {args.text}")

        elif args.command == "translate":
            result = translate_text(args.text, args.to)
            print(result)

        elif args.command == "vision":
            result = analyze_image(args.image)
            print(result)

        elif args.command == "ask":
            result = answer_question(args.question)
            print(result)

        elif args.command == "helmet":
            print("Activating Helmet Mode...")
            helmet_mode()

        elif args.command == "design":
            print(design_ascii(args.text, args.style))

        elif args.command == "weather":
            print(get_weather(args.city))

        elif args.command == "config":
            if args.set:
                key, value = args.set.split("=", 1)
                cfg = load_config(args.file)
                section = cfg.setdefault("friday", {})
                section[key] = value
                save_config(cfg, args.file)
                print(f"Config set: {key}={value}")
            elif args.get:
                cfg = load_config(args.file)
                print(cfg.get("friday", {}).get(args.get, ""))
            else:
                print("Usage: friday config --set KEY=VALUE | --get KEY [--file PATH]")
                return 1

        elif args.command == "backup":
            print(backup_db())

        elif args.command == "restore":
            print(restore_db(args.file))

        elif args.command == "habit":
            if args.add:
                habit_id = add_habit(conn, user_id, args.add)
                print(f"Habit added: {args.add} [{habit_id}]")
            elif args.complete:
                complete_habit(conn, args.complete)
                print(f"Habit {args.complete} completed")
            elif args.list:
                habits = get_habits(conn, user_id)
                for h in habits:
                    print(f"[{h[0]}] {h[1]} ({h[2]}) streak={h[3]} best={h[4]}")
            else:
                print("Usage: friday habit --add NAME | --complete ID | --list")
                return 1

        elif args.command == "shopping":
            if args.add:
                item_id = add_shopping_item(conn, user_id, args.add)
                print(f"Shopping item added: {args.add} [{item_id}]")
            elif args.toggle:
                toggle_shopping_item(conn, args.toggle)
                print(f"Shopping item {args.toggle} toggled")
            elif args.list:
                items = get_shopping_items(conn, user_id)
                for s in items:
                    status = "bought" if s[3] else "pending"
                    print(f"[{s[0]}] {s[1]} x{s[2]} ({status})")
            else:
                print("Usage: friday shopping --add ITEM | --toggle ID | --list")
                return 1

        elif args.command == "recipe":
            if args.add:
                recipe_id = add_recipe(conn, user_id, args.add)
                print(f"Recipe added: {args.add} [{recipe_id}]")
            elif args.ingredient:
                recipe_id = int(args.ingredient) if args.ingredient.isdigit() else None
                if recipe_id and args.amount:
                    add_recipe_ingredient(conn, recipe_id, args.ingredient, args.amount)
                    print(f"Ingredient added to recipe {recipe_id}")
                else:
                    print("Usage: friday recipe --ingredient NAME --amount AMOUNT --list")
                    return 1
            elif args.list:
                recipes = get_recipes(conn, user_id)
                for r in recipes:
                    print(f"[{r[0]}] {r[1]} (servings: {r[3]})")
            else:
                print("Usage: friday recipe --add NAME | --ingredient NAME --amount AMOUNT | --list")
                return 1

        elif args.command == "pomodoro":
            if args.start:
                session_id = start_pomodoro(conn, user_id, args.start)
                print(f"Pomodoro started: {args.start} [{session_id}]")
            elif args.stop:
                end_pomodoro(conn, args.stop)
                print(f"Pomodoro {args.stop} stopped")
            elif args.list:
                sessions = get_pomodoro_sessions(conn, user_id)
                for p in sessions:
                    print(f"[{p[0]}] {p[1] or 'focus'} {p[2]} -> {p[3] or 'running'}")
            else:
                print("Usage: friday pomodoro --start [TASK] | --stop ID | --list")
                return 1

        else:
            if hasattr(args, 'command') and args.command is None:
                parser.print_help()
            return 1
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
