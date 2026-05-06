from flask import Flask, request, jsonify, render_template_string
import json
import os

app = Flask(__name__)

# --- BACKEND DATABASE LOGIC ---
DB_FILE = 'database.json'

def load_data():
    if not os.path.exists(DB_FILE):
        initial_data = {
            "users": {"admin": "1234"},
            "userStats": {"admin": {"attempts": 0, "bestWpm": 0, "accuracy": 0}}
        }
        save_data(initial_data)
        return initial_data
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- ROUTES ---

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
    db['userStats'][u] = {"attempts": 0, "bestWpm": 0, "accuracy": 0}
    save_data(db)
    return jsonify({"status": "success"})

@app.route('/api/update_stats', methods=['POST'])
def update_stats():
    data = request.json
    db = load_data()
    u = data.get('u')
    if u in db['userStats']:
        db['userStats'][u]['attempts'] += 1
        if data.get('wpm') > db['userStats'][u]['bestWpm']:
            db['userStats'][u]['bestWpm'] = data.get('wpm')
        db['userStats'][u]['accuracy'] = data.get('acc')
        save_data(db)
    return jsonify({"status": "success"})

@app.route('/api/admin_data')
def admin_data():
    db = load_data()
    return jsonify(db['userStats'])

# --- HTML / JS CODE ---
HTML_CODE = """
<!DOCTYPE html>  <html>  
<head>  
<title>Beginner Typing Speed Test</title>  
<link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@500&family=Pacifico&display=swap" rel="stylesheet">  
<style>  
:root { --bg: #1a1a2e; --text: white; --primary: #00c6ff; }
body { margin:0; font-family:'Roboto Mono', monospace; background: var(--bg); color: var(--text); overflow:hidden; transition: 0.3s; }  

/* Themes */
body.light-theme { --bg: #f0f2f5; --text: #1a1a2e; --primary: #0072ff; }
body.neon-theme { --bg: #000; --text: #0f0; --primary: #f0f; }
body.matrix-theme { --bg: #000; --text: #00ff41; --primary: #003b00; }

.left-menu{ position:fixed; top:120px; left:20px; display:flex; flex-direction:column; gap:10px; z-index:10000; }  
.left-menu button{ padding:10px; border:none; border-radius:6px; background: var(--primary); color: white; cursor:pointer; font-weight: bold; width: 140px; text-align: left; }  

.modal{ position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); background:rgba(10, 10, 30, 0.98); padding:30px; border-radius:15px; display:none; z-index:99999; min-width: 400px; max-width: 650px; border: 2px solid var(--primary); box-shadow: 0 0 30px rgba(0, 198, 255, 0.3); max-height: 85vh; overflow-y: auto; }  
.modal input, .modal select { width:100%; margin:10px 0; padding:10px; border:none; border-radius:5px; box-sizing: border-box; background: #222; color: white; }  

/* Learn Steps CSS */
.step-item { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #28a745; }
.video-frame { width: 100%; height: 250px; border-radius: 8px; margin-top: 10px; background: #000; }

#statsTable { margin-top: 20px; max-height: 300px; overflow-y: auto; }
table { width: 100%; border-collapse: collapse; color: white; font-size: 14px; }
th, td { border: 1px solid #333; padding: 12px; text-align: center; }
th { background: #0072ff; color: white; }
tr:nth-child(even) { background: rgba(255,255,255,0.05); }
.user-circle{ background: var(--primary); padding:8px 15px; border-radius:20px; }  

#welcomeScreen{ position:fixed; top:0; left:0; width:100%; height:100%; background:linear-gradient(135deg,#000428,#004e92); display:flex; justify-content:center; align-items:center; flex-direction:column; z-index:100000; }  
#welcomeText{ font-size:45px; font-family:'Pacifico', cursive; color:#00ffff; text-shadow:0 0 20px #00ffff; }  
.start-btn{ margin-top:20px; padding:12px 25px; border:none; border-radius:10px; background:linear-gradient(45deg,#00c6ff,#0072ff); color:white; cursor:pointer; font-size:16px; }  
.header { width:100%; display:flex; justify-content:space-between; padding:20px 50px; background:rgba(0,0,0,0.3); position:fixed; top:0; font-family:'Pacifico', cursive; box-sizing: border-box; }  
.header h2{color:#00ffff; margin:0;}  
.center { position:absolute; top:55%; left:50%; transform:translate(-50%,-50%); width:80%; text-align:center; }  
#task { font-size:32px; line-height:2; color:#aaa; }  
.correct {color:#00ff88;}  
.wrong {color:#ff4d4d;}  
#hiddenInput { opacity:0; position:absolute; }  
#timer { font-size:28px; color:#00ffcc; text-shadow:0 0 10px #00ffff; margin-bottom:15px; }  
.btn { margin:10px; padding:12px 30px; border:none; border-radius:10px; background:linear-gradient(45deg,#00c6ff,#0072ff); color:white; font-size:16px; cursor:pointer; }  

#finishOverlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(10, 10, 30, 0.95); display: none; justify-content: center; align-items: center; flex-direction: column; z-index: 200000; text-align: center; }
#finishOverlay h1 { font-family: 'Pacifico', cursive; color: #00ffff; font-size: 60px; margin: 0; }
#finalScore { font-size: 28px; color: #00ff88; margin: 20px 0; }
</style>  </head>  <body onclick="focusInput(); unlockAudio();">  

<div id="finishOverlay">
    <h1>Congratulations! 🚀</h1>
    <div id="finalScore"></div>
    <div style="display:flex; gap:10px;">
        <button class="btn" onclick="nextLevel()">Next Level</button>
        <button class="btn" style="background:gray;" onclick="restartTest()">Restart</button>
    </div>
</div>

<div class="left-menu">  
<button onclick="showTest()">Test ⏱</button>  
<button onclick="openLogin()">Login 👤</button>  
<button onclick="openCreate()">Create Account ✨</button>  
<button onclick="openAdmin()" style="background:#ff4d4d;">ADMIN PANEL 📊</button>
<button onclick="openSettings()" style="background:#ffa500;">SETTINGS ⚙️</button>
<button onclick="openLearn()" style="background:#28a745;">LEARN 🎓</button>
</div>  

<div class="modal" id="learnBox" onclick="event.stopPropagation()">
    <h2 style="color: #28a745">Typing Mastery (Step-by-Step)</h2>
    
    <div class="step-item">
        <h3>Step 1: Finger Positioning (Beginner)</h3>
        <p>Position your fingers on the 'Home Row'. Use 3D animation to understand the base layout.</p>
        <iframe class="video-frame" src="https://www.youtube.com/embed/1ArVtCQqQRE" frameborder="0" allowfullscreen></iframe>
    </div>

    <div class="step-item">
        <h3>Step 2: Key Mapping (Intermediate)</h3>
        <p>Learn which finger is responsible for which key without looking down.</p>
        <iframe class="video-frame" src="https://www.youtube.com/embed/6_f7SreQ59U" frameborder="0" allowfullscreen></iframe>
    </div>

    <div class="step-item">
        <h3>Step 3: 100+ WPM Secrets (Advanced)</h3>
        <p>Advanced 3D techniques for maximum speed and zero errors.</p>
        <iframe class="video-frame" src="https://www.youtube.com/embed/Xm_66o70o0M" frameborder="0" allowfullscreen></iframe>
    </div>

    <button class="btn" onclick="closeAll()">Start Practice</button>
</div>

<div class="modal" id="settingsBox" onclick="event.stopPropagation()">
    <h2 style="color: var(--primary)">Settings</h2>
    <label>Theme:</label>
    <select id="themeSelect" onchange="changeTheme()">
        <option value="default">Midnight Dark</option>
        <option value="light-theme">Arctic White</option>
        <option value="neon-theme">Neon Glow</option>
        <option value="matrix-theme">The Matrix</option>
    </select>
    <label>Audio:</label>
    <select id="audioSelect">
        <option value="classic">Classic Square</option>
        <option value="mechanical">Mechanical Keyboard</option>
        <option value="silent">No Sound</option>
    </select>
    <br><br>
    <button class="btn" onclick="closeAll()">Save & Close</button>
</div>

<div class="modal" id="loginBox" onclick="event.stopPropagation()">  
<h3>Login</h3>  <input type="text" id="username" placeholder="Username"> <input type="password" id="password" placeholder="Password">  
<button class="btn" onclick="login()">Login</button> <button class="btn" style="background:gray" onclick="closeAll()">Close</button>
</div>  

<div class="modal" id="createBox" onclick="event.stopPropagation()">  
<h3>Create Account</h3> <input type="text" id="newUsername" placeholder="Username"> <input type="password" id="newPassword" placeholder="Password">  
<button class="btn" onclick="createAccount()">Create</button> <button class="btn" style="background:gray" onclick="closeAll()">Close</button>
</div>  

<div class="modal" id="adminPanel" onclick="event.stopPropagation()">
    <h2 style="color:#00ffff">Admin Leaderboard</h2> <div id="statsTable"></div> <br> <button class="btn" onclick="closeAll()">Close</button>
</div>

<div id="welcomeScreen">  
    <div id="welcomeText">Welcome 🚀</div>  
    <button class="start-btn" onclick="startSite()">Start</button>  
</div>  

<div class="header">  
<h2>Typing Speed Test</h2>  
<div id="userDisplay"></div>  
</div>  

<div class="center">  
<div id="timer"></div>  
<div id="task"></div>  
<input id="hiddenInput">  
<div id="result"></div>  
<div id="gameButtons" style="display:none;">  
<button class="btn" onclick="nextLevel()">Next Level</button>  
<button class="btn" onclick="restartTest()" style="background:gray;">Restart</button>  
</div>  
</div>  

<div class="test-box" id="testBox" style="display:none; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); background:rgba(255,255,255,0.1); padding:25px; border-radius:15px; text-align:center; z-index: 50000;">  
<h2>Select Time</h2>  
<button class="btn" onclick="startTest(60)">1 Min</button>  <button class="btn" onclick="startTest(180)">3 Min</button> <button class="btn" onclick="startTest(300)">5 Min</button>  
</div>  

<script>  
let currentUser = null, currentLevelIndex = 0, isPaused = false, testRunning = false;
let audioCtx, timer, timeLeft=60, startTime, totalTyped=0, currentText="";

const typingLevels = [
    "Technology is evolving rapidly in today's world.",
    "Efficient typing skills are essential for productivity in the modern digital era.",
    "The quick brown fox jumps over the lazy dog while the sun sets behind the green hills."
];

function closeAll(){  
    ['loginBox', 'createBox', 'settingsBox', 'adminPanel', 'learnBox', 'testBox', 'finishOverlay'].forEach(id => {
        let el = document.getElementById(id); if(el) el.style.display="none";
    });
}  

function openLearn() { stopTyping(); closeAll(); document.getElementById('learnBox').style.display="block"; }
function openSettings() { stopTyping(); closeAll(); settingsBox.style.display="block"; }
function changeTheme() { document.body.className = document.getElementById("themeSelect").value; }

function openLogin(){ stopTyping(); closeAll(); loginBox.style.display="block"; username.focus(); }  
async function login(){  
    let u = username.value, p = password.value;  
    const res = await fetch('/api/login', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({u, p})});
    if(res.ok){ currentUser = u; userDisplay.innerHTML = "<span class='user-circle'>👤 "+u+"</span>"; closeAll(); } 
    else alert("Login Failed");  
}  
function openCreate(){ stopTyping(); closeAll(); createBox.style.display="block"; }  
async function createAccount(){  
    let u = newUsername.value, p = newPassword.value;
    const res = await fetch('/api/create', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({u, p})});
    if(res.ok) alert("Created!"); closeAll();
}
async function openAdmin(){
    stopTyping(); closeAll(); adminPanel.style.display="block";
    const res = await fetch('/api/admin_data'); const data = await res.json();
    let html = "<table><tr><th>User</th><th>Max WPM</th></tr>";
    for(let u in data) { html += `<tr><td>${u}</td><td>${data[u].bestWpm}</td></tr>`; }
    statsTable.innerHTML = html + "</table>";
}

function stopTyping(){ clearInterval(timer); isPaused = true; }  

window.addEventListener("keydown", (e) => {
    if(e.code === "Space" && isPaused && testRunning) { isPaused = false; timer = setInterval(updateTimer, 1000); }
    if(e.code === "Enter" && testRunning) finishTest();
});

function loadText(){  
    closeAll(); currentText = typingLevels[currentLevelIndex % typingLevels.length]; 
    let html=""; for(let char of currentText) html += `<span>${char}</span>`;
    task.innerHTML = html; hiddenInput.value = ""; startTime = new Date().getTime();  
    isPaused = false; testRunning = true; clearInterval(timer); timer = setInterval(updateTimer, 1000);  
}  

function updateTimer(){ if(!isPaused){ timeLeft--; document.getElementById("timer").innerText="⏱ "+timeLeft+" sec"; if(timeLeft<=0) finishTest(); } }  

hiddenInput.addEventListener("input", function() {  
    if(isPaused || !testRunning) return;
    playKeySound(); let input=this.value, spans=document.querySelectorAll("#task span"); totalTyped=input.length;  
    spans.forEach((s, i) => { if(input[i]==null) s.className=""; else s.className=(input[i]===currentText[i])?"correct":"wrong"; });
    if(input===currentText) finishTest();  
});  

async function finishTest(){  
    clearInterval(timer); testRunning = false;
    let wpm = Math.round((totalTyped/5)/((new Date().getTime()-startTime)/60000)) || 0;
    finalScore.innerText = "Speed: " + wpm + " WPM";
    finishOverlay.style.display = "flex";
    if(currentUser) await fetch('/api/update_stats', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({u: currentUser, wpm: wpm, acc: 100})});
}  

function nextLevel() { currentLevelIndex++; timeLeft=60; loadText(); }
function restartTest() { timeLeft=60; loadText(); }
function showTest(){ stopTyping(); closeAll(); testBox.style.display="block"; }  
function startTest(t){ timeLeft=t; loadText(); }  
function startSite(){ welcomeScreen.style.display="none"; loadText(); }  
function focusInput(){ if(testRunning) hiddenInput.focus(); }
function unlockAudio(){ if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)(); }
function playKeySound(){ 
    let type = audioSelect.value; if(!audioCtx || type === 'silent') return;
    let osc = audioCtx.createOscillator(); let gain = audioCtx.createGain();
    osc.type = type === 'mechanical' ? 'sawtooth' : 'square';
    osc.frequency.value = 180 + Math.random()*60;
    gain.gain.value = 0.03; osc.connect(gain); gain.connect(audioCtx.destination);
    osc.start(); osc.stop(audioCtx.currentTime + 0.05);
}
</script>  
</body>  
</html>  
"""

if __name__ == "__main__":
    app.run(debug=True)
