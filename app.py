from flask import Flask, request, jsonify, render_template_string
import json
import os
from datetime import datetime

app = Flask(__name__)
DB_FILE = 'database.json'

def load_data():
    if not os.path.exists(DB_FILE):
        initial_data = {
            "users": {"admin": "Admin@1234"},  # Updated default password to match new strong policy
            "userStats": {"admin": {"attempts": 0, "bestWpm": 0, "accuracy": 0, "history": []}}
        }
        save_data(initial_data)
        return initial_data
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    db = load_data()
    u, p = data.get('u'), data.get('p')
    if db['users'].get(u) == p:
        return jsonify({"status": "success", "stats": db['userStats'].get(u, {})})
    return jsonify({"status": "fail"}), 401

@app.route('/api/create', methods=['POST'])
def create():
    data = request.json
    db = load_data()
    u, p = data.get('u'), data.get('p')
    if u in db['users']:
        return jsonify({"status": "exists"}), 400
    db['users'][u] = p
    db['userStats'][u] = {"attempts": 0, "bestWpm": 0, "accuracy": 0, "history": []}
    save_data(db)
    return jsonify({"status": "success"})

@app.route('/api/update_stats', methods=['POST'])
def update_stats():
    data = request.json
    db = load_data()
    u = data.get('u')
    if u in db['userStats']:
        if 'history' not in db['userStats'][u]:
            db['userStats'][u]['history'] = []
            
        db['userStats'][u]['attempts'] += 1
        if data.get('wpm') > db['userStats'][u]['bestWpm']:
            db['userStats'][u]['bestWpm'] = data.get('wpm')
        db['userStats'][u]['accuracy'] = data.get('acc')
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_entry = {
            "date_time": current_time,
            "wpm": data.get('wpm'),
            "accuracy": data.get('acc')
        }
        db['userStats'][u]['history'].append(history_entry)
        save_data(db)
    return jsonify({"status": "success"})

@app.route('/api/admin_data')
def admin_data():
    db = load_data()
    return jsonify(db['userStats'])

# ==================== FRONTEND (HTML, CSS, JS) ====================
HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Beginner Typing Speed Test</title>
    <style>
        :root {
            --bg: #1a1a2e;
            --panel-bg: #162447;
            --accent: #e43f5a;
            --text: #ffffff;
            --text-muted: #bdc3c7;
        }
        .theme-arctic {
            --bg: #f5f6fa;
            --panel-bg: #dcdde1;
            --accent: #2f3640;
            --text: #2f3640;
            --text-muted: #718093;
        }
        .theme-neon {
            --bg: #0d0d0d;
            --panel-bg: #1a1a1a;
            --accent: #00ffcc;
            --text: #00ffcc;
            --text-muted: #009977;
        }
        .theme-matrix {
            --bg: #000000;
            --panel-bg: #051105;
            --accent: #00ff00;
            --text: #00ff00;
            --text-muted: #005500;
        }

        body {
            background-color: var(--bg);
            color: var(--text);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            display: flex;
            height: 100vh;
            overflow: hidden;
            transition: all 0.3s ease;
        }

        .left-menu {
            width: 220px;
            background-color: var(--panel-bg);
            display: flex;
            flex-direction: column;
            padding: 20px 10px;
            box-shadow: 2px 0 10px rgba(0,0,0,0.3);
        }

        .left-menu button {
            background: transparent;
            border: 2px solid transparent;
            color: var(--text);
            padding: 12px 15px;
            margin: 8px 0;
            text-align: left;
            font-size: 16px;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.2s;
        }

        .left-menu button:hover, .left-menu button.active {
            border-color: var(--accent);
            background: rgba(255,255,255,0.05);
        }

        .main-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 40px;
            position: relative;
        }

        #welcomeScreen {
            text-align: center;
        }

        .start-btn {
            background-color: var(--accent);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 20px;
            border-radius: 30px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }

        #testArea {
            display: none;
            width: 100%;
            max-width: 800px;
            text-align: center;
        }

        .stats-bar {
            display: flex;
            justify-content: space-around;
            width: 100%;
            margin-bottom: 30px;
            font-size: 20px;
            font-weight: bold;
        }

        .text-display {
            background-color: var(--panel-bg);
            padding: 25px;
            border-radius: 12px;
            font-size: 24px;
            line-height: 1.6;
            letter-spacing: 1px;
            text-align: left;
            margin-bottom: 20px;
            min-height: 100px;
            word-wrap: break-word;
        }

        .text-display span {
            position: relative;
            color: var(--text-muted);
        }

        .text-display span.correct { color: #00ff88; }
        .text-display span.wrong { color: #ff4d4d; background-color: rgba(255,77,77,0.1); }
        .text-display span.current { border-left: 2px solid var(--accent); animation: blink 0.8s infinite; }

        @keyframes blink { 50% { border-color: transparent; } }

        #hiddenInput { position: absolute; opacity: 0; z-index: -1; }

        /* Modal Styles */
        .modal {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: var(--panel-bg);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            z-index: 100;
            width: 90%;
            max-width: 450px;
        }

        .modal-header { font-size: 22px; margin-bottom: 20px; font-weight: bold; }
        .modal input {
            width: 93%; padding: 12px; margin-bottom: 15px;
            background: rgba(0,0,0,0.2); border: 1px solid var(--text-muted);
            color: var(--text); border-radius: 6px;
        }
        .modal button {
            background-color: var(--accent); color: white; border: none;
            padding: 12px 25px; border-radius: 6px; cursor: pointer; width: 100%; font-size: 16px;
        }
        .close-modal {
            position: absolute; top: 15px; right: 15px; cursor: pointer; font-size: 20px;
        }

        /* Overlay Congratulations Page */
        #finishOverlay {
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: var(--bg);
            z-index: 200;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
        }

        .filter-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        .filter-buttons button {
            background: rgba(255,255,255,0.1);
            color: var(--text);
            border: 1px solid var(--text-muted);
            padding: 5px 12px;
            cursor: pointer;
            border-radius: 4px;
        }
        .filter-buttons button.active {
            background: var(--accent);
            border-color: var(--accent);
        }

        #leaderboardBody tr:nth-child(1) { background: rgba(241, 196, 15, 0.2); font-weight: bold; }
        #leaderboardBody tr:nth-child(2) { background: rgba(149, 165, 166, 0.2); }
        #leaderboardBody tr:nth-child(3) { background: rgba(211, 84, 0, 0.2); }
    </style>
</head>
<body>

    <input type="text" id="hiddenInput" autocomplete="off">

    <div class="left-menu">
        <h2 style="text-align: center; margin-bottom: 30px;">TypeMaster</h2>
        <button id="menuTest" class="active" onclick="showSection('test')">Typing Test</button>
        <button id="menuLogin" onclick="openAuthModal()">Login / Register</button>
        <button id="menuAdmin" onclick="openAdmin()">Admin Panel</button>
        <button id="menuLearn" onclick="openModal('learnBox')">Learn Typing</button>
        <button id="menuSettings" onclick="openModal('settingsBox')">Settings</button>
        <div id="userDisplay" style="margin-top: auto; text-align: center; font-weight: bold; color: var(--accent);"></div>
    </div>

    <div class="main-container">
        <!-- Welcome Screen -->
        <div id="welcomeScreen">
            <h1 style="font-size: 45px; margin-bottom: 10px;">Test Your Typing Speed</h1>
            <p style="color: var(--text-muted); margin-bottom: 30px;">Accurate real-time analytics to improve your speed.</p>
            <button class="start-btn" onclick="startTestFlow()">Start Practice 🚀</button>
        </div>

        <!-- Testing Area -->
        <div id="testArea">
            <div class="stats-bar">
                <div>Level: <span id="statLevel">1</span>/5</div>
                <div>Time: <span id="statTime">60</span>s</div>
                <div>WPM: <span id="statWpm">0</span></div>
                <div>Accuracy: <span id="statAcc">100</span>%</div>
            </div>
            <div class="text-display" id="textDisplay" onclick="focusHiddenInput()"></div>
            <p style="color: var(--text-muted);" id="pauseNotice">Press [Space] to resume if paused. Press [Enter] to instantly finish.</p>
        </div>
    </div>

    <!-- Auth Modal (Login / Register) -->
    <div class="modal" id="authModal">
        <span class="close-modal" onclick="closeModal('authModal')">&times;</span>
        <div id="loginView">
            <div class="modal-header">Login</div>
            <input type="text" id="loginUser" placeholder="Username">
            <input type="password" id="loginPass" placeholder="Password">
            <button onclick="login()">Login</button>
            <p style="text-align:center; margin-top:15px; cursor:pointer; font-size:14px;" onclick="toggleAuthView(false)">Don't have an account? Register</p>
        </div>
        <div id="registerView" style="display: none;">
            <div class="modal-header">Create Account</div>
            <input type="text" id="regUser" placeholder="Username (Min 8 Letters)">
            <input type="password" id="regPass" placeholder="Strong Password">
            <button onclick="createAccount()">Register</button>
            <p style="text-align:center; margin-top:15px; cursor:pointer; font-size:14px;" onclick="toggleAuthView(true)">Already have an account? Login</p>
        </div>
    </div>

    <!-- Admin Modal -->
    <div class="modal" id="adminPanel" style="max-width: 600px;">
        <span class="close-modal" onclick="closeModal('adminPanel')">&times;</span>
        <div class="modal-header">Leaderboard & Stats</div>
        
        <div class="filter-buttons">
            <button id="filter-all" class="active" onclick="filterAdminData('all')">All Time</button>
            <button id="filter-1" onclick="filterAdminData(1)">1 Day</button>
            <button id="filter-30" onclick="filterAdminData(30)">1 Month</button>
            <button id="filter-365" onclick="filterAdminData(365)">1 Year</button>
        </div>

        <div style="max-height: 300px; overflow-y: auto;">
            <table style="width: 100%; border-collapse: collapse; text-align: left;">
                <thead>
                    <tr style="border-bottom: 2px solid var(--accent);">
                        <th style="padding: 8px;">Rank</th>
                        <th style="padding: 8px;">User</th>
                        <th style="padding: 8px;">Attempts</th>
                        <th style="padding: 8px;">Best WPM</th>
                        <th style="padding: 8px;">Last Accuracy</th>
                    </tr>
                </thead>
                <tbody id="leaderboardBody"></tbody>
            </table>
        </div>
    </div>

    <!-- Settings Modal -->
    <div class="modal" id="settingsBox">
        <span class="close-modal" onclick="closeModal('settingsBox')">&times;</span>
        <div class="modal-header">Preferences</div>
        <label>Visual Theme:</label>
        <select id="themeSelect" onchange="changeTheme()" style="width:100%; padding:10px; margin: 10px 0 20px; background:#000; color:#fff; border:1px solid var(--text-muted); border-radius:6px;">
            <option value="dark">Midnight Dark</option>
            <option value="arctic">Arctic White</option>
            <option value="neon">Neon Glow</option>
            <option value="matrix">The Matrix</option>
        </select>
        <label>Keyboard Sound:</label>
        <select id="soundSelect" style="width:100%; padding:10px; margin: 10px 0; background:#000; color:#fff; border:1px solid var(--text-muted); border-radius:6px;">
            <option value="mechanical">Mechanical Click</option>
            <option value="classic">Classic Beep</option>
            <option value="none">Mute</option>
        </select>
    </div>

    <!-- Learn Typing Modal -->
    <div class="modal" id="learnBox" style="max-width: 500px;">
        <span class="close-modal" onclick="closeModal('learnBox')">&times;</span>
        <div class="modal-header">Learn Proper Finger Positioning</div>
        <div style="position:relative; padding-bottom:56.25%; height:0; overflow:hidden; border-radius:8px;">
            <iframe style="position:absolute; top:0; left:0; width:100%; height:100%;" src="https://www.youtube.com/embed/Sk8IQooXvYk" frameborder="0" allowfullscreen></iframe>
        </div>
        <p style="font-size: 14px; margin-top: 15px; color: var(--text-muted);">Keep your wrists straight, place fingers on the Home Row (ASDF JKL;), and practice without looking down.</p>
    </div>

    <!-- Full Screen Finish Overlay -->
    <div id="finishOverlay">
        <h1 style="font-size: 50px; color: #00ff88; margin-bottom: 10px;">Congratulations! 🚀</h1>
        <p style="font-size: 20px; margin-bottom: 30px;">Practice makes perfect. Here is your evaluation:</p>
        <div style="display:flex; gap: 40px; margin-bottom: 40px;">
            <div>
                <div style="font-size: 14px; color: var(--text-muted);">SPEED</div>
                <div style="font-size: 45px; font-weight:bold;" id="overWpm">0 WPM</div>
            </div>
            <div>
                <div style="font-size: 14px; color: var(--text-muted);">ACCURACY</div>
                <div style="font-size: 45px; font-weight:bold;" id="overAcc">100%</div>
            </div>
        </div>
        <button class="start-btn" onclick="nextLevelOrRestart()">Continue Progress</button>
    </div>

    <script>
        let currentUser = null;
        let currentLevelIndex = 0;
        let timer = null;
        let timeLeft = 60;
        let testRunning = false;
        let isPaused = false;
        let globalUserStats = {};

        const typingLevels = [
            "The quick brown fox jumps over the lazy dog perfectly.",
            "Success is not final failure is not fatal it is the courage to continue that counts.",
            "Develop a passion for learning If you do you will never cease to grow in your life.",
            "Technology is best when it brings people together and solves real world problems safely.",
            "Artificial intelligence and computer networking systems are shaping the landscape of modern tech architectures."
        ];

        let currentText = typingLevels[0];
        const hiddenInput = document.getElementById('hiddenInput');
        const textDisplay = document.getElementById('textDisplay');

        // Audio System
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function playKeySound() {
            const soundType = document.getElementById('soundSelect').value;
            if (soundType === 'none') return;

            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);

            if (soundType === 'mechanical') {
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(120, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(10, audioCtx.currentTime + 0.05);
                gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
                gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.05);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.05);
            } else {
                osc.type = 'square';
                osc.frequency.setValueAtTime(600, audioCtx.currentTime);
                gain.gain.setValueAtTime(0.05, audioCtx.currentTime);
                gain.gain.linearRampToValueAtTime(0.001, audioCtx.currentTime + 0.03);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.03);
            }
        }

        // Setup text view
        function setupTextDisplay() {
            textDisplay.innerHTML = '';
            for (let char of currentText) {
                const span = document.createElement('span');
                span.innerText = char;
                textDisplay.appendChild(span);
            }
            if(textDisplay.children.length > 0) textDisplay.children[0].classList.add('current');
        }

        function startTestFlow() {
            document.getElementById('welcomeScreen').style.display = 'none';
            document.getElementById('testArea').style.display = 'block';
            resetTest();
            focusHiddenInput();
        }

        function focusHiddenInput() {
            if (!isPaused) hiddenInput.focus();
        }

        function resetTest() {
            clearInterval(timer);
            timeLeft = 60;
            testRunning = false;
            isPaused = false;
            hiddenInput.value = '';
            document.getElementById('statTime').innerText = timeLeft;
            document.getElementById('statWpm').innerText = '0';
            document.getElementById('statAcc').innerText = '100';
            document.getElementById('pauseNotice').style.visibility = 'hidden';
            setupTextDisplay();
        }

        function startTimer() {
            testRunning = true;
            timer = setInterval(() => {
                if (!isPaused) {
                    timeLeft--;
                    document.getElementById('statTime').innerText = timeLeft;
                    calculateRealtimeStats();
                    if (timeLeft <= 0) finishTest();
                }
            }, 1000);
        }

        function pauseTyping() {
            isPaused = true;
            document.getElementById('pauseNotice').innerText = "Test Paused. Press [Space] to resume.";
            document.getElementById('pauseNotice').style.visibility = 'visible';
        }

        function resumeTyping() {
            isPaused = false;
            document.getElementById('pauseNotice').style.visibility = 'hidden';
            hiddenInput.focus();
        }

        hiddenInput.addEventListener('input', () => {
            if (!testRunning && !isPaused) startTimer();
            if (isPaused) {
                hiddenInput.value = hiddenInput.value.slice(0, -1);
                return;
            }

            playKeySound();
            const inputVal = hiddenInput.value;
            const spans = textDisplay.children;
            let correctCount = 0;

            for (let i = 0; i < spans.length; i++) {
                spans[i].className = '';
                if (i < inputVal.length) {
                    if (inputVal[i] === currentText[i]) {
                        spans[i].classList.add('correct');
                        correctCount++;
                    } else {
                        spans[i].classList.add('wrong');
                    }
                }
            }

            if (inputVal.length < spans.length) {
                spans[inputVal.length].classList.add('current');
            }

            // Detect if idle/pause threshold hit (e.g. trailing space or logic checking)
            if (inputVal.endsWith('   ')) { 
                pauseTyping();
            }

            if (inputVal.length >= currentText.length) {
                finishTest();
            }
        });

        // Key interception for Pausing (Space) and Instant Finishing (Enter)
        window.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && isPaused) {
                e.preventDefault();
                resumeTyping();
            }
            if (e.code === 'Enter' && testRunning) {
                e.preventDefault();
                finishTest();
            }
        });

        function calculateRealtimeStats() {
            const inputVal = hiddenInput.value;
            if (inputVal.length === 0) return;
            const timeUsed = (60 - timeLeft) / 60;
            if (timeUsed <= 0) return;

            let correct = 0;
            for(let i=0; i<inputVal.length; i++) {
                if(inputVal[i] === currentText[i]) correct++;
            }

            const wpm = Math.round((inputVal.length / 5) / timeUsed);
            const acc = Math.round((correct / inputVal.length) * 100);

            document.getElementById('statWpm').innerText = wpm;
            document.getElementById('statAcc').innerText = acc;
        }

        async function finishTest() {
            clearInterval(timer);
            testRunning = false;
            const inputVal = hiddenInput.value;
            const timeUsed = Math.max(1, 60 - timeLeft);
            
            let correct = 0;
            for(let i=0; i<inputVal.length; i++) {
                if(inputVal[i] === currentText[i]) correct++;
            }

            const finalWpm = Math.round((inputVal.length / 5) / (timeUsed / 60)) || 0;
            const finalAcc = inputVal.length > 0 ? Math.round((correct / inputVal.length) * 100) : 0;

            document.getElementById('overWpm').innerText = finalWpm + " WPM";
            document.getElementById('overAcc').innerText = finalAcc + "%";
            document.getElementById('finishOverlay').style.display = 'flex';

            if (currentUser) {
                await fetch('/api/update_stats', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ u: currentUser, wpm: finalWpm, acc: finalAcc })
                });
            }
        }

        function nextLevelOrRestart() {
            document.getElementById('finishOverlay').style.display = 'none';
            currentLevelIndex = (currentLevelIndex + 1) % typingLevels.length;
            currentText = typingLevels[currentLevelIndex];
            document.getElementById('statLevel').innerText = currentLevelIndex + 1;
            resetTest();
            focusHiddenInput();
        }

        // Modals Management
        function openModal(id) { document.getElementById(id).style.display = 'block'; }
        function closeModal(id) { document.getElementById(id).style.display = 'none'; }
        function openAuthModal() { openModal('authModal'); toggleAuthView(true); }
        function toggleAuthView(showLogin) {
            document.getElementById('loginView').style.display = showLogin ? 'block' : 'none';
            document.getElementById('registerView').style.display = showLogin ? 'none' : 'block';
        }

        async function login() {
            const u = document.getElementById('loginUser').value.trim();
            const p = document.getElementById('loginPass').value.trim();
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ u, p })
            });
            if (res.ok) {
                currentUser = u;
                document.getElementById('userDisplay').innerText = `Active: ${u}`;
                closeModal('authModal');
                alert('Successfully logged in!');
            } else {
                alert('Invalid Credentials');
            }
        }

        async function createAccount() {
            const u = document.getElementById('regUser').value.trim();
            const p = document.getElementById('regPass').value.trim();

            // 1. Username Length Validation (Minimum 8 characters)
            if (u.length < 8) {
                alert("Username must be at least 8 characters long!");
                return;
            }

            // 2. Strong Password Validation via RegEx
            // Must contain: 8 Chars minimum, 1 Uppercase letter, 1 Number, 1 Special Char
            const strongPasswordRegex = /^(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*])(?=.{8,})/;

            if (!strongPasswordRegex.test(p)) {
                alert("Password is too weak!\n\nIt must contain:\n- At least 8 characters\n- One Uppercase letter (A-Z)\n- One Number (0-9)\n- One Special Character (!@#$%^&*)");
                return;
            }

            const res = await fetch('/api/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ u, p })
            });
            const data = await res.json();
            if (data.status === 'exists') {
                alert('Username already taken!');
            } else {
                alert('Account verified and created successfully! You can login now.');
                toggleAuthView(true);
            }
        }

        async function openAdmin() {
            const res = await fetch('/api/admin_data');
            globalUserStats = await res.json();
            openModal('adminPanel');
            filterAdminData('all');
        }

        function filterAdminData(filterType) {
            // Adjust active filter class
            document.querySelectorAll('.filter-buttons button').forEach(b => b.classList.remove('active'));
            if(filterType === 'all') document.getElementById('filter-all').classList.add('active');
            else if(filterType === 1) document.getElementById('filter-1').classList.add('active');
            else if(filterType === 30) document.getElementById('filter-30').classList.add('active');
            else if(filterType === 365) document.getElementById('filter-365').classList.add('active');

            const tbody = document.getElementById('leaderboardBody');
            tbody.innerHTML = '';

            let processedUsers = [];

            for (let username in globalUserStats) {
                let userData = globalUserStats[username];
                let attempts = 0;
                let bestWpm = 0;
                let lastAccuracy = 0;

                if (filterType === 'all') {
                    attempts = userData.attempts;
                    bestWpm = userData.bestWpm;
                    lastAccuracy = userData.accuracy;
                } else {
                    let filteredHistory = (userData.history || []).filter(entry => {
                        let entryDate = new Date(entry.date_time.replace(' ', 'T'));
                        let timeDiff = new Date() - entryDate;
                        let daysDiff = timeDiff / (1000 * 60 * 60 * 24);
                        return daysDiff <= filterType;
                    });

                    attempts = filteredHistory.length;
                    if (attempts > 0) {
                        bestWpm = Math.max(...filteredHistory.map(h => h.wpm));
                        lastAccuracy = filteredHistory[filteredHistory.length - 1].accuracy;
                    }
                }

                if (filterType === 'all' || attempts > 0) {
                    processedUsers.push({
                        username, attempts, bestWpm, lastAccuracy
                    });
                }
            }

            processedUsers.sort((a, b) => b.bestWpm - a.bestWpm);

            processedUsers.forEach((user, index) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="padding: 8px;">#${index + 1}</td>
                    <td style="padding: 8px;">${user.username}</td>
                    <td style="padding: 8px;">${user.attempts}</td>
                    <td style="padding: 8px;">${user.bestWpm}</td>
                    <td style="padding: 8px;">${user.lastAccuracy}%</td>
                `;
                tbody.appendChild(tr);
            });
        }

        function changeTheme() {
            const theme = document.getElementById('themeSelect').value;
            document.body.className = '';
            if (theme !== 'dark') document.body.classList.add(`theme-${theme}`);
        }

        setupTextDisplay();
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)
