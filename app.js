/* ============================================================
   FRIDAY ASSISTANT - MAIN APPLICATION
   ============================================================ */

// ========================
// GLOBAL STATE
// ========================
const State = {
  currentModule: 'chat',
  helmetMode: false,
  tvMode: false,
  voiceActive: false,
  recognition: null,
  synthesis: window.speechSynthesis,
  myNumber: '6043282162',
  contacts: [
    { id: 1, name: 'Mom', number: '+16043282162', initials: 'M' },
    { id: 2, name: 'John', number: '+15551234567', initials: 'J' },
    { id: 3, name: 'Sarah', number: '+15559876543', initials: 'S' },
  ],
  schedule: [
    { id: 1, time: '09:00', title: 'Morning Briefing', desc: 'Daily review with team', day: 'today' },
    { id: 2, time: '11:30', title: 'Lunch with Mark', desc: 'At the usual spot', day: 'today' },
    { id: 3, time: '14:00', title: 'Design Review', desc: 'Project Alpha milestone', day: 'today' },
    { id: 4, time: '17:00', title: 'Gym Session', desc: 'Leg day 💪', day: 'today' },
    { id: 5, time: '19:00', title: 'Dinner', desc: 'Reservation at 7:30pm', day: 'today' },
  ],
  steps: { current: 6847, goal: 10000 },
  bookings: [
    { id: 1, title: 'Dentist', date: '2026-09-02T10:00', location: 'Downtown Dental', status: 'confirmed' },
    { id: 2, title: 'Haircut', date: '2026-09-05T14:30', location: 'Style Studio', status: 'pending' },
  ],
  messages: [
    { from: 'Mom', text: 'Don\'t forget dinner tonight!', time: '2h ago', type: 'incoming' },
    { from: 'John', text: 'Can you send me the file?', time: '5h ago', type: 'incoming' },
    { from: 'Sarah', text: 'See you at 3!', time: '1d ago', type: 'incoming' },
  ],
};

// ========================
// UTILITIES
// ========================
function $(id) { return document.getElementById(id); }
function qs(sel) { return document.querySelector(sel); }
function qsa(sel) { return document.querySelectorAll(sel); }
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
function showToast(message, type = 'info') {
  const container = $('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => { toast.remove(); }, 3500);
}
function formatDate(d) {
  return d.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' });
}
function formatTime(d) {
  return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

// ========================
// SPEECH
// ========================
function speak(text) {
  if (!State.synthesis) return;
  State.synthesis.cancel();
  const utter = new SpeechSynthesisUtterance(text);
  utter.rate = 1; utter.pitch = 1; utter.volume = 1;
  // Try to pick a good voice
  const voices = State.synthesis.getVoices();
  const preferred = voices.find(v => v.name.includes('Google') && v.lang.startsWith('en')) || voices[0];
  if (preferred) utter.voice = preferred;
  State.synthesis.speak(utter);
}

function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    console.warn('Speech recognition not supported');
    return;
  }
  State.recognition = new SpeechRecognition();
  State.recognition.continuous = false;
  State.recognition.interimResults = false;
  State.recognition.lang = 'en-US';

  State.recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    processVoiceCommand(transcript);
    stopListening();
  };

  State.recognition.onerror = (event) => {
    console.error('Speech error:', event.error);
    stopListening();
  };

  State.recognition.onend = () => stopListening();
}

function startListening() {
  if (!State.recognition) { showToast('Voice recognition not supported', 'error'); return; }
  State.voiceActive = true;
  $('voiceIndicator').classList.remove('hidden');
  try { State.recognition.start(); } catch (e) { /* already started */ }
}

function stopListening() {
  State.voiceActive = false;
  $('voiceIndicator').classList.add('hidden');
  try { State.recognition.stop(); } catch (e) {}
}

// ========================
// AI RESPONSE ENGINE
// ========================
function getAIResponse(input) {
  const lower = input.toLowerCase();

  // Greetings
  if (/^(hi|hello|hey|good\s*(morning|afternoon|evening)|howdy)/i.test(lower)) {
    const greetings = ['Hello! How can I assist you today?', 'Hey there! Ready to help.', 'Greetings! What\'s on your mind?'];
    return greetings[Math.floor(Math.random() * greetings.length)];
  }

  // Schedule queries
  if (lower.includes('today') || lower.includes('schedule') || lower.includes('calendar') || lower.includes('appointment') || lower.includes('plan')) {
    const todayItems = State.schedule.filter(s => s.day === 'today');
    if (todayItems.length === 0) return 'You have nothing scheduled for today.';
    let resp = `You have ${todayItems.length} items today:\n`;
    todayItems.forEach(item => { resp += `• ${item.time} - ${item.title}: ${item.desc}\n`; });
    return resp.trim();
  }

  // Steps
  if (lower.includes('step') || lower.includes('walk') || lower.includes('exercise')) {
    const pct = Math.round((State.steps.current / State.steps.goal) * 100);
    return `You've taken ${State.steps.current.toLocaleString()} steps today (${pct}% of your ${State.steps.goal.toLocaleString()} step goal). Keep going!`;
  }

  // Call
  if (lower.includes('call') || lower.includes('phone')) {
    const contact = State.contacts.find(c => lower.includes(c.name.toLowerCase()));
    if (contact) return `Calling ${contact.name} at ${contact.number}... (simulated)`;
    return 'Who would you like me to call?';
  }

  // Message
  if (lower.includes('message') || lower.includes('text') || lower.includes('sms')) {
    const contact = State.contacts.find(c => lower.includes(c.name.toLowerCase()));
    if (contact) return `Messaging ${contact.name}... (simulated)`;
    return 'Who would you like to message?';
  }

  // Instagram
  if (lower.includes('instagram')) return 'Opening Instagram... (simulated browser view)';

  // Snapchat
  if (lower.includes('snapchat') || lower.includes('snap')) return 'Opening Snapchat... (simulated)';

  // Google / Search
  if (lower.includes('google') || lower.includes('search')) {
    const query = input.replace(/google|search/gi, '').trim();
    if (query) return `Searching Google for "${query}"... (results below in Search tab)`;
    return 'What would you like me to search for?';
  }

  // YouTube
  if (lower.includes('youtube')) {
    const query = input.replace(/youtube/gi, '').trim();
    return query ? `Playing "${query}" on YouTube... (simulated)` : 'Opening YouTube...';
  }

  // Design
  if (lower.includes('design') || lower.includes('draw') || lower.includes('sketch')) {
    return 'Opening the design canvas. What would you like me to design?';
  }

  // Book appointment
  if (lower.includes('book') || lower.includes('appointment')) {
    return 'Opening the booking form. What kind of appointment would you like to schedule?';
  }

  // Translate
  if (lower.includes('translate') || lower.includes('translation')) {
    return 'Opening translation. Please enter text to translate.';
  }

  // Vision / Photo
  if (lower.includes('picture') || lower.includes('photo') || lower.includes('image') || lower.includes('ocean') || lower.includes('depth')) {
    return 'Opening vision analysis. Upload a photo and I\'ll analyze it for you.';
  }

  // Helmet mode
  if (lower.includes('helmet') || lower.includes('iron man') || lower.includes('jarvis')) {
    toggleHelmet();
    return 'Activating Helmet Mode. JARVIS online.';
  }

  // TV remote
  if (lower.includes('tv') || lower.includes('remote')) {
    toggleTV();
    return 'Opening Google TV Remote.';
  }

  // Identity
  if (lower.includes('who are you') || lower.includes('your name')) return 'I\'m Friday, your personal AI assistant. I\'m here 24/7 to help with anything you need.';

  // Time
  if (lower.includes('time')) return `It's currently ${formatTime(new Date())}.`;

  // Date
  if (lower.includes('date') || lower.includes('day')) return `Today is ${formatDate(new Date())}.`;

  // Ocean depth (general knowledge)
  if (lower.includes('ocean') || lower.includes('deep') || lower.includes('water')) {
    if (lower.includes('deepest') || lower.includes('how deep')) {
      return 'The deepest point in the ocean is the Challenger Deep in the Mariana Trench, at approximately 10,984 meters (36,037 feet) deep. For comparison, if you placed Mount Everest there, its peak would still be over 2 kilometers underwater.';
    }
    return 'The average depth of the ocean is about 3,688 meters (12,100 feet). The deepest known point is the Challenger Deep at roughly 10,984 meters.';
  }

  // Help
  if (lower.includes('help') || lower.includes('what can you do')) {
    return 'I can help with: Schedule, Steps, Contacts/Calls, Social Media (Instagram, Snapchat), Google & YouTube Search, Design, Appointments, Translations, Vision/Photo Analysis, and Helmet Mode. Just ask!';
  }

  // Default
  const defaults = [
    'I understand. How else can I help you today?',
    'Noted. Is there anything specific you\'d like me to do?',
    'I\'m here to help. Try asking about your schedule, steps, or any of my other features.',
    'Got it. You can ask me to call someone, check your schedule, search the web, and much more.',
  ];
  return defaults[Math.floor(Math.random() * defaults.length)];
}

function processVoiceCommand(transcript) {
  addChatMessage(transcript, 'user');
  setTimeout(() => {
    const response = getAIResponse(transcript);
    addChatMessage(response, 'assistant');
    speak(response);
  }, 400);
}

// ========================
// CHAT MODULE
// ========================
function renderChat() {
  const area = $('contentArea');
  area.innerHTML = `
    <div class="module" data-module="chat">
      <h2>FRIDAY <span class="sub">Voice & Chat Assistant</span></h2>
      <div class="chat-container">
        <div class="chat-messages" id="chatMessages"></div>
        <div class="chat-input-row">
          <input type="text" id="chatInput" placeholder="Ask Friday anything…" autocomplete="off" />
          <button class="icon-btn" id="voiceBtn" title="Voice Input">🎙</button>
          <button class="btn btn-sm" id="chatSend">SEND</button>
        </div>
      </div>
    </div>
  `;

  const msgs = $('chatMessages');
  const input = $('chatInput');
  const sendBtn = $('chatSend');
  const voiceBtn = $('voiceBtn');

  // Initial greeting
  const initialMsg = 'Hello! I\'m Friday, your personal assistant. I can help with your schedule, steps, calls, messages, social media, search, design, bookings, translations, and more. What can I do for you?';
  setTimeout(() => {
    addChatMessage(initialMsg, 'assistant', msgs);
    speak(initialMsg);
  }, 1200);

  function sendMessage() {
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    addChatMessage(text, 'user', msgs);
    setTimeout(() => {
      const response = getAIResponse(text);
      addChatMessage(response, 'assistant', msgs);
      speak(response);
    }, 500);
  }

  sendBtn.onclick = sendMessage;
  input.onkeydown = (e) => { if (e.key === 'Enter') sendMessage(); };

  voiceBtn.onclick = () => {
    if (State.voiceActive) { stopListening(); voiceBtn.classList.remove('recording'); }
    else { startListening(); voiceBtn.classList.add('recording'); }
  };

  // Handle commands from other modules
  window.sendChatMessage = (text) => {
    addChatMessage(text, 'user', msgs);
    setTimeout(() => {
      const response = getAIResponse(text);
      addChatMessage(response, 'assistant', msgs);
      speak(response);
    }, 400);
  };
}

function addChatMessage(text, sender, container) {
  const msgs = container || $('chatMessages');
  if (!msgs) return;
  const div = document.createElement('div');
  div.className = `chat-msg ${sender}`;
  div.innerHTML = `<div class="chat-bubble">${escapeHtml(text).replace(/\n/g, '<br>')}</div>`;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}

// ========================
// SCHEDULE MODULE
// ========================
function renderSchedule() {
  const area = $('contentArea');
  const items = State.schedule.filter(s => s.day === 'today');
  area.innerHTML = `
    <div class="module" data-module="schedule">
      <h2>SCHEDULE <span class="sub">Today's Plan</span></h2>
      <div style="margin-bottom:16px;display:flex;gap:8px;flex-wrap:wrap;">
        <input type="text" id="schedTime" placeholder="Time (e.g. 10:00)" style="width:120px;" />
        <input type="text" id="schedTitle" placeholder="Event title" style="flex:1;min-width:180px;" />
        <input type="text" id="schedDesc" placeholder="Description" style="flex:1;min-width:180px;" />
        <button class="btn btn-sm" id="addSched">ADD</button>
      </div>
      <div class="schedule-grid" id="scheduleGrid"></div>
    </div>
  `;
  refreshScheduleGrid();

  $('addSched').onclick = () => {
    const time = $('schedTime').value.trim();
    const title = $('schedTitle').value.trim();
    const desc = $('schedDesc').value.trim();
    if (!time || !title) { showToast('Please fill in time and title', 'error'); return; }
    State.schedule.push({ id: Date.now(), time, title, desc: desc || '', day: 'today' });
    $('schedTime').value = ''; $('schedTitle').value = ''; $('schedDesc').value = '';
    refreshScheduleGrid();
    showToast('Event added', 'success');
  };
}

function refreshScheduleGrid() {
  const grid = $('scheduleGrid');
  if (!grid) return;
  const items = State.schedule.filter(s => s.day === 'today');
  if (items.length === 0) { grid.innerHTML = '<p style="color:var(--text-3)">No events scheduled for today.</p>'; return; }
  grid.innerHTML = items.map(item => `
    <div class="schedule-item">
      <div class="schedule-time">${escapeHtml(item.time)}</div>
      <div class="schedule-title">${escapeHtml(item.title)}</div>
      <div class="schedule-desc">${escapeHtml(item.desc)}</div>
    </div>
  `).join('');
}

// ========================
// STEPS MODULE
// ========================
function renderSteps() {
  const area = $('contentArea');
  const pct = Math.min(100, Math.round((State.steps.current / State.steps.goal) * 100));
  const circumference = 2 * Math.PI * 80;
  const offset = circumference - (pct / 100) * circumference;
  area.innerHTML = `
    <div class="module" data-module="steps">
      <h2>STEPS <span class="sub">Daily Activity</span></h2>
      <div class="steps-display">
        <div class="steps-ring">
          <svg width="200" height="200" viewBox="0 0 200 200">
            <circle class="steps-bg" cx="100" cy="100" r="80" />
            <circle class="steps-fill" cx="100" cy="100" r="80"
              stroke-dasharray="${circumference}"
              stroke-dashoffset="${offset}" />
          </svg>
          <div class="steps-number">${State.steps.current.toLocaleString()}</div>
        </div>
        <div class="steps-goal">Goal: ${State.steps.goal.toLocaleString()} steps (${pct}%)</div>
        <div class="steps-actions">
          <button class="btn btn-sm" id="addSteps">+1,000</button>
          <button class="btn btn-sm" id="addSteps5k">+5,000</button>
          <button class="btn btn-sm btn-gold" id="resetSteps">RESET</button>
        </div>
      </div>
      <div class="card" style="margin-top:20px;">
        <div class="card-header">Activity Stats</div>
        <div class="card-row"><span class="card-label">Steps Today</span><span class="card-value">${State.steps.current.toLocaleString()}</span></div>
        <div class="card-row"><span class="card-label">Distance (est.)</span><span class="card-value">${(State.steps.current * 0.000762).toFixed(2)} km</span></div>
        <div class="card-row"><span class="card-label">Calories (est.)</span><span class="card-value">${Math.round(State.steps.current * 0.04)} kcal</span></div>
        <div class="card-row"><span class="card-label">Goal Progress</span><span class="card-value">${pct}%</span></div>
      </div>
    </div>
  `;
  $('addSteps').onclick = () => { State.steps.current += 1000; renderSteps(); };
  $('addSteps5k').onclick = () => { State.steps.current += 5000; renderSteps(); };
  $('resetSteps').onclick = () => { State.steps.current = 0; renderSteps(); };
}

// ========================
// CONTACTS MODULE
// ========================
function renderContacts() {
  const area = $('contentArea');
  area.innerHTML = `
    <div class="module" data-module="contacts">
      <h2>CONTACTS <span class="sub">Call & Message</span></h2>
      <div style="margin-bottom:16px;display:flex;gap:8px;flex-wrap:wrap;">
        <input type="text" id="newContactName" placeholder="Name" style="width:150px;" />
        <input type="text" id="newContactNumber" placeholder="Number" style="width:180px;" />
        <button class="btn btn-sm" id="addContact">ADD</button>
      </div>
      <div class="contact-list" id="contactList"></div>
      <div class="card" style="margin-top:20px;">
        <div class="card-header">My Number</div>
        <div class="card-row"><span class="card-label">Primary</span><span class="card-value">${State.myNumber}</span></div>
        <p style="font-size:.8rem;color:var(--text-3);margin-top:8px;">This number is registered for messages and voicemails.</p>
      </div>
    </div>
  `;
  refreshContactList();

  $('addContact').onclick = () => {
    const name = $('newContactName').value.trim();
    const number = $('newContactNumber').value.trim();
    if (!name || !number) { showToast('Fill in name and number', 'error'); return; }
    State.contacts.push({ id: Date.now(), name, number, initials: name[0].toUpperCase() });
    $('newContactName').value = ''; $('newContactNumber').value = '';
    refreshContactList();
    showToast('Contact added', 'success');
  };
}

function refreshContactList() {
  const list = $('contactList');
  if (!list) return;
  list.innerHTML = State.contacts.map(c => `
    <div class="contact-item">
      <div class="contact-avatar">${c.initials}</div>
      <div class="contact-info">
        <div class="contact-name">${escapeHtml(c.name)}</div>
        <div class="contact-number">${escapeHtml(c.number)}</div>
      </div>
      <div class="contact-actions">
        <button class="call-btn" onclick="callContact('${escapeHtml(c.name)}', '${escapeHtml(c.number)}')" title="Call">📞</button>
        <button class="msg-btn" onclick="msgContact('${escapeHtml(c.name)}')" title="Message">✉</button>
      </div>
    </div>
  `).join('');
}

window.callContact = (name, number) => {
  showToast(`Calling ${name} at ${number}... (simulated)`, 'info');
  speak(`Calling ${name}`);
};
window.msgContact = (name) => {
  showToast(`Messaging ${name}... (simulated)`, 'info');
};

// ========================
// SOCIAL MODULE
// ========================
function renderSocial() {
  const area = $('contentArea');
  area.innerHTML = `
    <div class="module" data-module="social">
      <h2>SOCIAL <span class="sub">Instagram & Snapchat</span></h2>
      <div class="social-grid">
        <div class="social-card" onclick="openSocial('instagram')">
          <div class="social-icon">📸</div>
          <div class="social-name">Instagram</div>
          <div class="social-desc">View feed, stories & reels</div>
        </div>
        <div class="social-card" onclick="openSocial('snapchat')">
          <div class="social-icon">👻</div>
          <div class="social-name">Snapchat</div>
          <div class="social-desc">Snap stories & chat</div>
        </div>
        <div class="social-card" onclick="openSocial('twitter')">
          <div class="social-icon">🐦</div>
          <div class="social-name">X / Twitter</div>
          <div class="social-desc">Trends & timeline</div>
        </div>
        <div class="social-card" onclick="openSocial('tiktok')">
          <div class="social-icon">🎵</div>
          <div class="social-name">TikTok</div>
          <div class="social-desc">Short videos & trends</div>
        </div>
      </div>
    </div>
  `;
}

window.openSocial = (platform) => {
  showToast(`Opening ${platform.charAt(0).toUpperCase() + platform.slice(1)}... (simulated)`, 'info');
  speak(`Opening ${platform}`);
};

// ========================
// SEARCH MODULE
// ========================
function renderSearch() {
  const area = $('contentArea');
  area.innerHTML = `
    <div class="module" data-module="search">
      <h2>SEARCH <span class="sub">Google & YouTube</span></h2>
      <div class="search-box">
        <input type="text" id="searchInput" placeholder="Search Google or paste a YouTube link…" />
        <button class="btn btn-sm" id="searchBtn">SEARCH</button>
        <button class="btn btn-sm btn-gold" id="ytBtn">▶ YOUTUBE</button>
      </div>
      <div class="search-results" id="searchResults"></div>
    </div>
  `;

  function doSearch() {
    const query = $('searchInput').value.trim();
    if (!query) return;
    const isYT = query.toLowerCase().includes('youtube') || query.startsWith('http');
    const results = $('searchResults');
    if (isYT) {
      results.innerHTML = `
        <div class="search-result" onclick="window.open('https://www.youtube.com/results?search_query=${encodeURIComponent(query)}','_blank')">
          <h4>▶ YouTube Search: "${escapeHtml(query)}"</h4>
          <p>Watch videos on YouTube</p>
          <div class="url">youtube.com</div>
        </div>`;
    } else {
      results.innerHTML = `
        <div class="search-result" onclick="window.open('https://www.google.com/search?q=${encodeURIComponent(query)}','_blank')">
          <h4>🔍 Google: "${escapeHtml(query)}"</h4>
          <p>Search the web for results</p>
          <div class="url">google.com</div>
        </div>
        <div class="search-result" onclick="window.open('https://www.youtube.com/results?search_query=${encodeURIComponent(query)}','_blank')">
          <h4>▶ YouTube: "${escapeHtml(query)}"</h4>
          <p>Watch videos related to your search</p>
          <div class="url">youtube.com</div>
        </div>`;
    }
  }

  $('searchBtn').onclick = doSearch;
  $('ytBtn').onclick = () => {
    const query = $('searchInput').value.trim() || 'music';
    window.open(`https://www.youtube.com/results?search_query=${encodeURIComponent(query)}`, '_blank');
  };
  $('searchInput').onkeydown = (e) => { if (e.key === 'Enter') doSearch(); };
}

// ========================
// DESIGN MODULE
// ========================
let designState = { tool: 'brush', color: '#ffb703', size: 4, drawing: false };

function renderDesign() {
  const area = $('contentArea');
  area.innerHTML = `
    <div class="module" data-module="design">
      <h2>DESIGN <span class="sub">Creative Canvas</span></h2>
      <div class="design-toolbar">
        <button class="tool-btn active" data-tool="brush">🖌 Brush</button>
        <button class="tool-btn" data-tool="line">📏 Line</button>
        <button class="tool-btn" data-tool="rect">⬜ Rect</button>
        <button class="tool-btn" data-tool="circle">⭕ Circle</button>
        <button class="tool-btn" data-tool="text">🔤 Text</button>
        <button class="tool-btn" data-tool="eraser">🧹 Eraser</button>
        <input type="color" id="designColor" value="#ffb703" />
        <input type="range" id="designSize" min="1" max="30" value="4" title="Size" />
        <button class="btn btn-sm btn-red" id="clearCanvas">CLEAR</button>
        <button class="btn btn-sm" id="saveCanvas">💾 SAVE</button>
      </div>
      <div class="design-canvas-wrap">
        <canvas id="designCanvas" class="design-canvas" height="500"></canvas>
      </div>
    </div>
  `;

  const canvas = $('designCanvas');
  const ctx = canvas.getContext('2d');
  canvas.width = canvas.parentElement.clientWidth;

  ctx.fillStyle = '#0a1120';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';

  // Toolbar handlers
  qsa('.tool-btn').forEach(btn => {
    btn.onclick = () => {
      qsa('.tool-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      designState.tool = btn.dataset.tool;
    };
  });

  $('designColor').oninput = (e) => { designState.color = e.target.value; };
  $('designSize').oninput = (e) => { designState.size = parseInt(e.target.value); };
  $('clearCanvas').onclick = () => { ctx.fillStyle = '#0a1120'; ctx.fillRect(0, 0, canvas.width, canvas.height); };
  $('saveCanvas').onclick = () => {
    const link = document.createElement('a');
    link.download = 'friday-design.png';
    link.href = canvas.toDataURL();
    link.click();
    showToast('Design saved!', 'success');
  };

  // Drawing
  let startX, startY, snapshot;

  function getPos(e) {
    const rect = canvas.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    return { x: clientX - rect.left, y: clientY - rect.top };
  }

  canvas.onmousedown = (e) => {
    designState.drawing = true;
    const pos = getPos(e);
    startX = pos.x; startY = pos.y;
    snapshot = ctx.getImageData(0, 0, canvas.width, canvas.height);
    ctx.beginPath(); ctx.moveTo(pos.x, pos.y);
  };
  canvas.onmousemove = (e) => {
    if (!designState.drawing) return;
    const pos = getPos(e);
    ctx.strokeStyle = designState.tool === 'eraser' ? '#0a1120' : designState.color;
    ctx.lineWidth = designState.tool === 'eraser' ? designState.size * 4 : designState.size;
    if (designState.tool === 'brush' || designState.tool === 'eraser') {
      ctx.lineTo(pos.x, pos.y);
      ctx.stroke();
    }
  };
  canvas.onmouseup = (e) => {
    if (!designState.drawing) return;
    designState.drawing = false;
    const pos = getPos(e);
    ctx.strokeStyle = designState.color;
    ctx.lineWidth = designState.size;
    if (designState.tool === 'rect') {
      ctx.putImageData(snapshot, 0, 0);
      ctx.strokeRect(startX, startY, pos.x - startX, pos.y - startY);
    } else if (designState.tool === 'circle') {
      ctx.putImageData(snapshot, 0, 0);
      const rx = Math.abs(pos.x - startX) / 2;
      const ry = Math.abs(pos.y - startY) / 2;
      const cx = startX + (pos.x - startX) / 2;
      const cy = startY + (pos.y - startY) / 2;
      ctx.beginPath(); ctx.ellipse(cx, cy, Math.max(1, rx), Math.max(1, ry), 0, 0, 2 * Math.PI); ctx.stroke();
    } else if (designState.tool === 'line') {
      ctx.putImageData(snapshot, 0, 0);
      ctx.beginPath(); ctx.moveTo(startX, startY); ctx.lineTo(pos.x, pos.y); ctx.stroke();
    }
  };
  canvas.onmouseleave = () => { designState.drawing = false; };
}

// ========================
// TRANSLATE MODULE
// ========================
function renderTranslate() {
  const area = $('contentArea');
  area.innerHTML = `
    <div class="module" data-module="translate">
      <h2>TRANSLATE <span class="sub">Multi-Language</span></h2>
      <div class="translate-box">
        <div>
          <label style="font-size:.75rem;color:var(--text-2);text-transform:uppercase;letter-spacing:2px;">From</label>
          <select id="fromLang">
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
            <option value="it">Italian</option>
            <option value="pt">Portuguese</option>
            <option value="ja">Japanese</option>
            <option value="ko">Korean</option>
            <option value="zh">Chinese</option>
            <option value="ar">Arabic</option>
            <option value="hi">Hindi</option>
            <option value="ru">Russian</option>
          </select>
          <textarea id="fromText" placeholder="Enter text to translate..."></textarea>
        </div>
        <div class="translate-actions">
          <button class="btn btn-gold" id="swapLang" style="height:40px;">⇄</button>
        </div>
        <div>
          <label style="font-size:.75rem;color:var(--text-2);text-transform:uppercase;letter-spacing:2px;">To</label>
          <select id="toLang">
            <option value="es">Spanish</option>
            <option value="en">English</option>
            <option value="fr">French</option>
            <option value="de">German</option>
            <option value="it">Italian</option>
            <option value="pt">Portuguese</option>
            <option value="ja">Japanese</option>
            <option value="ko">Korean</option>
            <option value="zh">Chinese</option>
            <option value="ar">Arabic</option>
            <option value="hi">Hindi</option>
            <option value="ru">Russian</option>
          </select>
          <textarea id="toText" placeholder="Translation..." readonly></textarea>
        </div>
      </div>
      <div style="margin-top:16px;">
        <button class="btn" id="translateBtn">TRANSLATE</button>
        <button class="btn btn-sm" id="speakFrom" style="margin-left:8px;">🔊</button>
        <button class="btn btn-sm" id="speakTo" style="margin-left:8px;">🔊</button>
      </div>
    </div>
  `;

  // Simple dictionary-based demo translations
  const dictionary = {
    'hello': { es: 'hola', fr: 'bonjour', de: 'hallo', it: 'ciao', pt: 'olá', ja: 'こんにちは', ko: '안녕하세요', zh: '你好', ar: 'مرحبا', hi: 'नमस्ते', ru: 'привет' },
    'thank you': { es: 'gracias', fr: 'merci', de: 'danke', it: 'grazie', pt: 'obrigado', ja: 'ありがとう', ko: '감사합니다', zh: '谢谢', ar: 'شكرا', hi: 'धन्यवाद', ru: 'спасибо' },
    'good morning': { es: 'buenos días', fr: 'bonjour', de: 'guten morgen', it: 'buongiorno', pt: 'bom dia', ja: 'おはよう', ko: '좋은 아침', zh: '早上好', ar: 'صباح الخير', hi: 'सुप्रभात', ru: 'доброе утро' },
    'good night': { es: 'buenas noches', fr: 'bonne nuit', de: 'gute nacht', it: 'buonanotte', pt: 'boa noite', ja: 'おやすみ', ko: '안녕히 주무세요', zh: '晚安', ar: 'تصبح على خير', hi: 'शुभ रात्रि', ru: 'спокойной ночи' },
    'how are you': { es: 'cómo estás', fr: 'comment allez-vous', de: 'wie geht es dir', it: 'come stai', pt: 'como vai', ja: 'お元気ですか', ko: '어떻게 지내세요', zh: '你好吗', ar: 'كيف حالك', hi: 'आप कैसे हैं', ru: 'как дела' },
  };

  $('translateBtn').onclick = () => {
    const from = $('fromText').value.trim().toLowerCase();
    const toLang = $('toLang').value;
    if (!from) { showToast('Enter text to translate', 'error'); return; }

    // Check dictionary
    const dictEntry = Object.entries(dictionary).find(([k]) => from === k || from.includes(k));
    let translation = '';
    if (dictEntry) {
      translation = dictEntry[1][toLang] || dictEntry[1]['en'] || dictEntry[0];
    } else {
      // Demo: just append language code
      const langNames = { es: '[ES]', fr: '[FR]', de: '[DE]', it: '[IT]', pt: '[PT]', ja: '[JA]', ko: '[KO]', zh: '[ZH]', ar: '[AR]', hi: '[HI]', ru: '[RU]', en: '[EN]' };
      translation = `[${langNames[toLang] || toLang.toUpperCase()}] ${from}`;
    }
    $('toText').value = translation;
    showToast('Translation complete', 'success');
  };

  $('speakFrom').onclick = () => { if ($('fromText').value) speak($('fromText').value); };
  $('speakTo').onclick = () => { if ($('toText').value) speak($('toText').value); };
}

// ========================
// VISION MODULE
// ========================
function renderVision() {
  const area = $('contentArea');
  area.innerHTML = `
    <div class="module" data-module="vision">
      <h2>VISION <span class="sub">Photo & Image Analysis</span></h2>
      <div class="vision-upload" id="visionUpload">
        <div class="upload-icon">📷</div>
        <div style="color:var(--text-2);font-size:.9rem;">Tap to upload a photo</div>
        <div style="color:var(--text-3);font-size:.75rem;">Supports ocean depth detection, Q&A, and more</div>
        <input type="file" id="visionFile" accept="image/*" style="display:none;" />
      </div>
      <div class="vision-preview hidden" id="visionPreview"></div>
      <div class="vision-result hidden" id="visionResult">
        <h4>ANALYSIS</h4>
        <p id="visionResultText"></p>
      </div>
    </div>
  `;

  const upload = $('visionUpload');
  const fileInput = $('visionFile');
  upload.onclick = () => fileInput.click();
  fileInput.onchange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      $('visionPreview').classList.remove('hidden');
      $('visionPreview').innerHTML = `<img src="${ev.target.result}" alt="Uploaded" />`;
      analyzeImage(file.name);
    };
    reader.readAsDataURL(file);
  };
}

function analyzeImage(filename) {
  const lower = filename.toLowerCase();
  let result = '';
  if (lower.includes('ocean') || lower.includes('sea') || lower.includes('water') || lower.includes('depth')) {
    result = 'Based on visual analysis, this appears to be an ocean/water scene. The average depth of the world\'s oceans is approximately 3,688 meters (12,100 feet). The Challenger Deep in the Mariana Trench reaches about 10,984 meters (36,037 feet) — deep enough to submerge Mount Everest with over 2 km to spare.';
  } else if (lower.includes('sky') || lower.includes('cloud')) {
    result = 'This appears to be a sky/cloud scene. I can identify cloud formations and atmospheric conditions. The sky appears clear with good visibility.';
  } else if (lower.includes('mountain') || lower.includes('hill')) {
    result = 'This appears to be a mountain or landscape scene. Terrain analysis suggests elevated geography with varied topography.';
  } else {
    result = 'Image analysis complete. I can see various elements in this photo. Ask me specific questions about what you\'d like to know, such as ocean depth, object identification, or scene description.';
  }
  $('visionResult').classList.remove('hidden');
  $('visionResultText').textContent = result;
}

// ========================
// BOOKINGS MODULE
// ========================
function renderBookings() {
  const area = $('contentArea');
  area.innerHTML = `
    <div class="module" data-module="bookings">
      <h2>BOOKINGS <span class="sub">Appointments</span></h2>
      <div class="booking-form">
        <label>Appointment Type</label>
        <input type="text" id="bookType" placeholder="e.g. Dentist, Haircut" />
        <label>Date & Time</label>
        <input type="datetime-local" id="bookDate" />
        <label>Location</label>
        <input type="text" id="bookLocation" placeholder="Address or place" />
        <button class="btn" id="bookBtn">BOOK APPOINTMENT</button>
      </div>
      <div class="booking-list" id="bookingList"></div>
    </div>
  `;
  refreshBookingList();

  $('bookBtn').onclick = () => {
    const type = $('bookType').value.trim();
    const date = $('bookDate').value;
    const location = $('bookLocation').value.trim();
    if (!type || !date) { showToast('Please fill in type and date', 'error'); return; }
    State.bookings.push({ id: Date.now(), title: type, date, location: location || 'TBD', status: 'confirmed' });
    $('bookType').value = ''; $('bookDate').value = ''; $('bookLocation').value = '';
    refreshBookingList();
    showToast('Appointment booked!', 'success');
  };
}

function refreshBookingList() {
  const list = $('bookingList');
  if (!list) return;
  if (State.bookings.length === 0) { list.innerHTML = '<p style="color:var(--text-3)">No upcoming bookings.</p>'; return; }
  list.innerHTML = State.bookings.map(b => `
    <div class="booking-item">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <div style="font-weight:700;color:var(--text-1);">${escapeHtml(b.title)}</div>
          <div style="font-size:.8rem;color:var(--text-3);">${new Date(b.date).toLocaleString()} • ${escapeHtml(b.location)}</div>
        </div>
        <span style="font-size:.7rem;color:var(--green);border:1px solid var(--green);padding:2px 8px;border-radius:10px;text-transform:uppercase;">${b.status}</span>
      </div>
    </div>
  `).join('');
}

// ========================
// HELMET MODE
// ========================
function toggleHelmet() {
  State.helmetMode = !State.helmetMode;
  const overlay = $('helmetOverlay');
  if (State.helmetMode) {
    overlay.classList.remove('hidden');
    startHelmetScan();
    showToast('Helmet Mode Activated', 'success');
  } else {
    overlay.classList.add('hidden');
    showToast('Helmet Mode Deactivated', 'info');
  }
}

function startHelmetScan() {
  const target = $('helmetTarget');
  const name = $('helmetTargetName');
  const dist = $('helmetDistance');
  if (!State.helmetMode) return;

  // Simulate scanning by moving target around
  const positions = [
    { x: 30, y: 20 }, { x: 60, y: 15 }, { x: 70, y: 40 },
    { x: 40, y: 60 }, { x: 55, y: 70 }, { x: 25, y: 45 },
  ];
  const labels = ['OBJECT', 'PERSON', 'VEHICLE', 'STRUCTURE', 'ANIMAL', 'DEVICE'];
  const distances = ['2.4m', '5.1m', '8.7m', '12.3m', '3.9m', '1.2m'];
  let idx = 0;

  setInterval(() => {
    if (!State.helmetMode) return;
    const p = positions[idx % positions.length];
    target.style.left = p.x + '%';
    target.style.top = p.y + '%';
    name.textContent = labels[idx % labels.length];
    dist.textContent = distances[idx % distances.length];
    idx++;
  }, 1500);
}

// ========================
// TV REMOTE
// ========================
function toggleTV() {
  State.tvMode = !State.tvMode;
  const overlay = $('tvOverlay');
  if (State.tvMode) {
    overlay.classList.remove('hidden');
    showToast('Google TV Remote Connected', 'success');
  } else {
    overlay.classList.add('hidden');
  }
}

function initTVRemote() {
  $('tvPower').onclick = () => { toggleTV(); showToast('TV power toggled', 'info'); };
  $('tvHome').onclick = () => showToast('TV: Home pressed', 'info');
  $('tvBack').onclick = () => showToast('TV: Back pressed', 'info');
  $('tvUp').onclick = () => showToast('TV: Up', 'info');
  $('tvDown').onclick = () => showToast('TV: Down', 'info');
  $('tvLeft').onclick = () => showToast('TV: Left', 'info');
  $('tvRight').onclick = () => showToast('TV: Right', 'info');
  $('tvOk').onclick = () => showToast('TV: OK', 'info');
  $('tvVolUp').onclick = () => showToast('TV: Volume Up', 'info');
  $('tvVolDown').onclick = () => showToast('TV: Volume Down', 'info');
  $('tvMute').onclick = () => showToast('TV: Mute', 'info');
  $('tvYT').onclick = () => { window.open('https://www.youtube.com', '_blank'); };
  $('tvSearch').onclick = () => switchModule('search');
  $('tvAssistant').onclick = () => { toggleTV(); switchModule('chat'); };
}

// ========================
// NAVIGATION
// ========================
const moduleRenderers = {
  chat: renderChat,
  schedule: renderSchedule,
  steps: renderSteps,
  contacts: renderContacts,
  social: renderSocial,
  search: renderSearch,
  design: renderDesign,
  translate: renderTranslate,
  vision: renderVision,
  bookings: renderBookings,
};

function switchModule(name) {
  State.currentModule = name;
  qsa('.nav-btn').forEach(b => b.classList.toggle('active', b.dataset.module === name));
  const renderer = moduleRenderers[name];
  if (renderer) renderer();
  $('contentArea').scrollTop = 0;
}

// ========================
// CLOCK
// ========================
function updateClock() {
  const now = new Date();
  const clock = $('hudClock');
  const date = $('hudDate');
  if (clock) clock.textContent = formatTime(now);
  if (date) date.textContent = formatDate(now);
}

// ========================
// INIT
// ========================
function init() {
  initSpeechRecognition();
  initTVRemote();

  // Clock
  updateClock();
  setInterval(updateClock, 1000);

  // Navigation
  qsa('.nav-btn').forEach(btn => {
    btn.onclick = () => switchModule(btn.dataset.module);
  });

  // Helmet toggle
  $('helmetToggle').onclick = toggleHelmet;
  $('tvRemoteToggle').onclick = toggleTV;

  // Power button
  $('powerBtn').onclick = () => {
    showToast('Friday is always on. Closing overlay…', 'info');
    if (State.helmetMode) toggleHelmet();
    if (State.tvMode) toggleTV();
  };

  // Splash screen
  setTimeout(() => {
    $('splash').classList.add('fade-out');
    setTimeout(() => {
      $('splash').classList.add('hidden');
      $('app').classList.remove('hidden');
      switchModule('chat');
    }, 800);
  }, 2200);

  // Handle window resize for canvas
  window.onresize = () => {
    if (State.currentModule === 'design') renderDesign();
  };
}

document.addEventListener('DOMContentLoaded', init);
