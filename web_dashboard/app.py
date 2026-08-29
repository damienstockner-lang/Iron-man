#!/usr/bin/env python3
import http.server
import socketserver
import json
import os
import sys
import webbrowser
import threading

# Add project root to path to import friday_assistant
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from friday_assistant.db import connect_db, setup_database, get_user_id
from friday_assistant.models import (
    add_task, complete_task, add_note, add_reminder, add_expense,
    record_steps, get_tasks, get_today_events, get_notes,
    get_stats, export_data, add_schedule_event, add_appointment,
    add_contact, find_contact, log_action, queue_tv_command,
)

MY_PHONE = "6043282162"
PORT = 8080

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Friday">
    <meta name="theme-color" content="#1e3c72">
    <link rel="manifest" href="/manifest.json">
    <link rel="apple-touch-icon" href="https://emoji.gg/assets/emoji/robot.png">
    <title>Friday Assistant Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle { font-size: 1.1em; opacity: 0.9; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.2s;
        }
        .card:hover { transform: translateY(-5px); }
        .card h2 {
            color: #1e3c72;
            margin-bottom: 15px;
            font-size: 1.5em;
            border-bottom: 2px solid #1e3c72;
            padding-bottom: 10px;
        }
        .form-group { margin-bottom: 15px; }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 600;
        }
        input, select, textarea {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #1e3c72;
        }
        button {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            width: 100%;
            transition: opacity 0.3s;
        }
        button:hover { opacity: 0.9; }
        .item-list {
            list-style: none;
            margin-top: 10px;
            max-height: 300px;
            overflow-y: auto;
        }
        .item-list li {
            padding: 10px;
            background: #f5f5f5;
            border-left: 4px solid #1e3c72;
            margin-bottom: 8px;
            border-radius: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-top: 15px;
        }
        .stat-box {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            display: block;
        }
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
        .nav {
            background: rgba(255,255,255,0.95);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .nav a {
            background: #1e3c72;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: opacity 0.3s;
        }
        .nav a:hover { opacity: 0.8; }
        .section { display: none; }
        .section.active { display: block; }
        .success {
            background: #d4edda;
            color: #155724;
            padding: 12px;
            border-radius: 8px;
            margin-top: 10px;
            border: 1px solid #c3e6cb;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 12px;
            border-radius: 8px;
            margin-top: 10px;
            border: 1px solid #f5c6cb;
        }
        .offline-badge {
            background: #ffc107;
            color: #333;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            display: inline-block;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 Friday Assistant <span class="offline-badge">OFFLINE MODE</span></h1>
            <p class="subtitle">Your Personal Command Center - No Internet Required</p>
        </header>

        <nav class="nav">
            <a href="#" onclick="showSection('dashboard')">📊 Dashboard</a>
            <a href="#" onclick="showSection('tasks')">✅ Tasks</a>
            <a href="#" onclick="showSection('notes')">📝 Notes</a>
            <a href="#" onclick="showSection('reminders')">⏰ Reminders</a>
            <a href="#" onclick="showSection('expenses')">💰 Expenses</a>
            <a href="#" onclick="showSection('steps')">👟 Steps</a>
            <a href="#" onclick="showSection('contacts')">👤 Contacts</a>
            <a href="#" onclick="showSection('export')">📤 Export</a>
        </nav>

        <!-- Dashboard Section -->
        <div id="dashboard" class="section active">
            <div class="card">
                <h2>📊 Statistics Overview</h2>
                <div class="stats-grid">
                    <div class="stat-box">
                        <span class="stat-number" id="stat-tasks">0</span>
                        <span class="stat-label">Total Tasks</span>
                    </div>
                    <div class="stat-box">
                        <span class="stat-number" id="stat-completed">0</span>
                        <span class="stat-label">Completed</span>
                    </div>
                    <div class="stat-box">
                        <span class="stat-number" id="stat-notes">0</span>
                        <span class="stat-label">Notes</span>
                    </div>
                    <div class="stat-box">
                        <span class="stat-number" id="stat-events">0</span>
                        <span class="stat-label">Events</span>
                    </div>
                    <div class="stat-box">
                        <span class="stat-number" id="stat-steps">0</span>
                        <span class="stat-label">Total Steps</span>
                    </div>
                    <div class="stat-box">
                        <span class="stat-number" id="stat-expenses">$0</span>
                        <span class="stat-label">Total Expenses</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tasks Section -->
        <div id="tasks" class="section">
            <div class="card">
                <h2>✅ Add New Task</h2>
                <form onsubmit="addTask(event)">
                    <div class="form-group">
                        <label>Task Title</label>
                        <input type="text" id="task-title" required>
                    </div>
                    <div class="form-group">
                        <label>Priority</label>
                        <select id="task-priority">
                            <option value="medium">Medium</option>
                            <option value="high">High</option>
                            <option value="low">Low</option>
                        </select>
                    </div>
                    <button type="submit">Add Task</button>
                </form>
                <ul class="item-list" id="task-list"></ul>
            </div>
        </div>

        <!-- Notes Section -->
        <div id="notes" class="section">
            <div class="card">
                <h2>📝 Add Note</h2>
                <form onsubmit="addNote(event)">
                    <div class="form-group">
                        <label>Note Content</label>
                        <textarea id="note-content" rows="3" required></textarea>
                    </div>
                    <div class="form-group">
                        <label>Tags (comma-separated)</label>
                        <input type="text" id="note-tags" placeholder="work, urgent">
                    </div>
                    <button type="submit">Add Note</button>
                </form>
                <ul class="item-list" id="note-list"></ul>
            </div>
        </div>

        <!-- Reminders Section -->
        <div id="reminders" class="section">
            <div class="card">
                <h2>⏰ Add Reminder</h2>
                <form onsubmit="addReminder(event)">
                    <div class="form-group">
                        <label>Reminder Title</label>
                        <input type="text" id="reminder-title" required>
                    </div>
                    <div class="form-group">
                        <label>Due Date/Time</label>
                        <input type="text" id="reminder-due" placeholder="2026-12-01T10:00:00">
                    </div>
                    <button type="submit">Add Reminder</button>
                </form>
            </div>
        </div>

        <!-- Expenses Section -->
        <div id="expenses" class="section">
            <div class="card">
                <h2>💰 Add Expense</h2>
                <form onsubmit="addExpense(event)">
                    <div class="form-group">
                        <label>Amount ($)</label>
                        <input type="number" step="0.01" id="expense-amount" required>
                    </div>
                    <div class="form-group">
                        <label>Category</label>
                        <input type="text" id="expense-category" placeholder="food, transport, etc.">
                    </div>
                    <div class="form-group">
                        <label>Note</label>
                        <input type="text" id="expense-note" placeholder="Optional note">
                    </div>
                    <button type="submit">Add Expense</button>
                </form>
            </div>
        </div>

        <!-- Steps Section -->
        <div id="steps" class="section">
            <div class="card">
                <h2>👟 Record Steps</h2>
                <form onsubmit="recordSteps(event)">
                    <div class="form-group">
                        <label>Step Count</label>
                        <input type="number" id="steps-count" required>
                    </div>
                    <button type="submit">Save Steps</button>
                </form>
            </div>
        </div>

        <!-- Contacts Section -->
        <div id="contacts" class="section">
            <div class="card">
                <h2>👤 Add Contact</h2>
                <form onsubmit="addContact(event)">
                    <div class="form-group">
                        <label>Name</label>
                        <input type="text" id="contact-name" required>
                    </div>
                    <div class="form-group">
                        <label>Phone</label>
                        <input type="text" id="contact-phone">
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" id="contact-email">
                    </div>
                    <button type="submit">Add Contact</button>
                </form>
            </div>
        </div>

        <!-- Export Section -->
        <div id="export" class="section">
            <div class="card">
                <h2>📤 Export Data</h2>
                <p style="margin-bottom: 15px; color: #666;">Download all your data as JSON.</p>
                <button onclick="exportData()">Export All Data</button>
                <pre id="export-output" style="margin-top: 15px; background: #f5f5f5; padding: 15px; border-radius: 8px; max-height: 400px; overflow-y: auto; display: none;"></pre>
            </div>
        </div>
    </div>

    <script>
        function showSection(id) {
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.getElementById(id).classList.add('active');
        }

        async function api(endpoint, data = {}) {
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                return await response.json();
            } catch (error) {
                console.error('API error:', error);
                return { error: error.message };
            }
        }

        async function addTask(e) {
            e.preventDefault();
            await api('/api/task', {
                title: document.getElementById('task-title').value,
                priority: document.getElementById('task-priority').value
            });
            loadTasks();
            loadStats();
            e.target.reset();
        }

        async function completeTask(id) {
            await api('/api/task/complete', { task_id: id });
            loadTasks();
            loadStats();
        }

        async function addNote(e) {
            e.preventDefault();
            await api('/api/note', {
                content: document.getElementById('note-content').value,
                tags: document.getElementById('note-tags').value
            });
            loadNotes();
            e.target.reset();
        }

        async function addReminder(e) {
            e.preventDefault();
            await api('/api/reminder', {
                title: document.getElementById('reminder-title').value,
                due_at: document.getElementById('reminder-due').value
            });
            alert('Reminder added!');
            e.target.reset();
        }

        async function addExpense(e) {
            e.preventDefault();
            await api('/api/expense', {
                amount: parseFloat(document.getElementById('expense-amount').value),
                category: document.getElementById('expense-category').value,
                note: document.getElementById('expense-note').value
            });
            alert('Expense added!');
            e.target.reset();
        }

        async function recordSteps(e) {
            e.preventDefault();
            await api('/api/steps', {
                count: parseInt(document.getElementById('steps-count').value)
            });
            loadStats();
            e.target.reset();
        }

        async function addContact(e) {
            e.preventDefault();
            await api('/api/contact', {
                name: document.getElementById('contact-name').value,
                phone: document.getElementById('contact-phone').value,
                email: document.getElementById('contact-email').value
            });
            alert('Contact added!');
            e.target.reset();
        }

        async function exportData() {
            const data = await api('/api/export');
            const output = document.getElementById('export-output');
            output.style.display = 'block';
            output.textContent = JSON.stringify(data, null, 2);
        }

        async function loadStats() {
            const data = await api('/api/stats');
            document.getElementById('stat-tasks').textContent = data.tasks_total || 0;
            document.getElementById('stat-completed').textContent = data.tasks_completed || 0;
            document.getElementById('stat-notes').textContent = data.notes || 0;
            document.getElementById('stat-events').textContent = data.events || 0;
            document.getElementById('stat-steps').textContent = data.total_steps || 0;
            document.getElementById('stat-expenses').textContent = '$' + (data.total_expenses || 0).toFixed(2);
        }

        async function loadTasks() {
            const data = await api('/api/tasks');
            const list = document.getElementById('task-list');
            if (!data.tasks || data.tasks.length === 0) {
                list.innerHTML = '<li>No tasks yet</li>';
                return;
            }
            list.innerHTML = data.tasks.map(t => `
                <li>
                    <span><strong>${t.title}</strong> - ${t.priority || 'medium'}</span>
                    ${t.is_completed ? '' : `<button onclick="completeTask(${t.task_id})">✓</button>`}
                </li>
            `).join('');
        }

        async function loadNotes() {
            const data = await api('/api/notes');
            const list = document.getElementById('note-list');
            if (!data.notes || data.notes.length === 0) {
                list.innerHTML = '<li>No notes yet</li>';
                return;
            }
            list.innerHTML = data.notes.map(n => `
                <li>
                    <span><strong>${n.content}</strong> ${n.tags ? '(' + n.tags + ')' : ''}</span>
                    <small>${n.created_at || ''}</small>
                </li>
            `).join('');
        }

        // Load data on page load
        loadStats();
        loadTasks();
        loadNotes();
    </script>
    <script>
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js').catch(() => {});
        }
    </script>
</body>
</html>
"""

class FridayHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode())
        elif self.path == '/manifest.json':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            with open(os.path.join(os.path.dirname(__file__), 'manifest.json'), 'rb') as f:
                self.wfile.write(f.read())
        elif self.path == '/sw.js':
            self.send_response(200)
            self.send_header('Content-type', 'application/javascript')
            self.end_headers()
            with open(os.path.join(os.path.dirname(__file__), 'sw.js'), 'rb') as f:
                self.wfile.write(f.read())
        elif self.path == '/api/stats':
            self.handle_stats()
        elif self.path == '/api/tasks':
            self.handle_tasks()
        elif self.path == '/api/notes':
            self.handle_notes()
        elif self.path == '/api/export':
            self.handle_export()
        else:
            super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode()) if post_data else {}
        except:
            data = {}

        if self.path == '/api/task':
            self.handle_add_task(data)
        elif self.path == '/api/task/complete':
            self.handle_complete_task(data)
        elif self.path == '/api/note':
            self.handle_add_note(data)
        elif self.path == '/api/reminder':
            self.handle_add_reminder(data)
        elif self.path == '/api/expense':
            self.handle_add_expense(data)
        elif self.path == '/api/steps':
            self.handle_steps(data)
        elif self.path == '/api/contact':
            self.handle_add_contact(data)
        else:
            self.send_json({"error": "Not found"}, 404)

    def send_json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def get_conn(self):
        conn = connect_db()
        setup_database(conn)
        return conn

    def handle_stats(self):
        conn = self.get_conn()
        user_id = get_user_id(conn, "Default User", "user@example.com", MY_PHONE)
        stats = get_stats(conn, user_id)
        conn.close()
        self.send_json(stats)

    def handle_tasks(self):
        conn = self.get_conn()
        user_id = get_user_id(conn, "Default User", "user@example.com", MY_PHONE)
        tasks = get_tasks(conn, user_id)
        conn.close()
        self.send_json({"tasks": [{"task_id": t[0], "title": t[1], "priority": t[5] if len(t) > 5 else "medium", "is_completed": t[3]} for t in tasks]})

    def handle_notes(self):
        conn = self.get_conn()
        user_id = get_user_id(conn, "Default User", "user@example.com", MY_PHONE)
        notes = get_notes(conn, user_id)
        conn.close()
        self.send_json({"notes": [{"note_id": n[0], "content": n[1], "created_at": n[2], "tags": n[3] if len(n) > 3 else None} for n in notes]})

    def handle_add_task(self, data):
        conn = self.get_conn()
        user_id = get_user_id(conn, "Default User", "user@example.com", MY_PHONE)
        add_task(conn, user_id, data.get("title", ""), priority=data.get("priority", "medium"))
        conn.close()
        self.send_json({"success": True})

    def handle_complete_task(self, data):
        conn = self.get_conn()
        complete_task(conn, data.get("task_id"))
        conn.close()
        self.send_json({"success": True})

    def handle_add_note(self, data):
        conn = self.get_conn()
        user_id = get_user_id(conn, "Default User", "user@example.com", MY_PHONE)
        add_note(conn, user_id, data.get("content", ""), data.get("tags"))
        conn.close()
        self.send_json({"success": True})

    def handle_add_reminder(self, data):
        conn = self.get_conn()
        user_id = get_user_id(conn, "Default User", "user@example.com", MY_PHONE)
        add_reminder(conn, user_id, data.get("title", ""), data.get("due_at", ""))
        conn.close()
        self.send_json({"success": True})

    def handle_add_expense(self, data):
        conn = self.get_conn()
        user_id = get_user_id(conn, "Default User", "user@example.com", MY_PHONE)
        add_expense(conn, user_id, float(data.get("amount", 0)), data.get("category"), data.get("note"))
        conn.close()
        self.send_json({"success": True})

    def handle_steps(self, data):
        conn = self.get_conn()
        record_steps(conn, int(data.get("count", 0)))
        conn.close()
        self.send_json({"success": True})

    def handle_add_contact(self, data):
        conn = self.get_conn()
        add_contact(conn, data.get("name", ""), data.get("phone"), data.get("email"))
        conn.close()
        self.send_json({"success": True})

    def handle_export(self):
        conn = self.get_conn()
        user_id = get_user_id(conn, "Default User", "user@example.com", MY_PHONE)
        data = export_data(conn, user_id)
        conn.close()
        self.send_json(data)

def main():
    with socketserver.TCPServer(("", PORT), FridayHTTPRequestHandler) as httpd:
        print(f"🚀 Friday Assistant Dashboard running at http://localhost:{PORT}")
        print(f"📱 Open your browser and go to: http://localhost:{PORT}")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Friday Dashboard stopped")

if __name__ == "__main__":
    main()
