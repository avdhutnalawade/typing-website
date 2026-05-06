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
<title>Pro Typing Speed Test</title>  
<link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@500&family=Pacifico&display=swap" rel="stylesheet">  
<style>  
:root { --bg: #1a1a2e; --text: white; --primary: #00c6ff; --accent: #00ff88; }
body { margin:0; font-family:'Roboto Mono', monospace; background: var(--bg); color: var(--text); overflow:hidden; transition: 0.3s; }  

/* Themes CSS */
body.light-theme { --bg: #f0f2f5; --text: #1a1a2e; --primary: #0072ff; }
body.neon-theme { --bg: #000; --text: #0f0; --primary: #f0f; --accent: #0ff; }
body.matrix-theme { --bg: #000; --text: #00ff41; --primary: #003b00; }

.left-menu{ position:fixed; top:120px; left:20px; display:flex; flex-direction:column; gap:10px; z-index:10000; }  
.left-menu button{ padding:10px; border:none; border-radius:6px; background: var(--primary); color: white; cursor:pointer; font-weight: bold; }  

.modal{ position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); background:rgba(10, 10, 30, 0.98); padding:30px; border-radius:15px; display:none; z-index:99999; min-width: 450px; border: 2px solid var(--primary); box-shadow: 0 0 30px rgba(0, 198, 255, 0.3); color: white; }  
.modal select, .modal input { width:100%; margin:10px 0; padding:10px; border-radius:5px; border:none; }

#statsTable { margin-top: 20px; max-height: 250px; overflow-y: auto; background: rgba(255,255,255,0.05); border-radius: 10px; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th, td { border: 1px solid #444; padding: 12px; text-align: center; }
th { background: var(--primary); color: white; }

#welcomeScreen{ position:fixed; top:0; left:0; width:100%; height:100%; background:linear-gradient(135deg,#000428,#004e92); display:flex; justify-content:center; align-items:center; flex-direction:column; z-index:100000; }  
#welcomeText{ font-size:45px; font-family:'Pacifico', cursive; color:#00ffff; text-shadow:0 0 20px #00ffff; }  
.start-btn{ margin-top:20px; padding:12px 25px; border:none; border-radius:10px; background:linear-gradient(45deg,#00c6ff,#0072ff); color:white; cursor:pointer; font-size:16px; }  

.header { width:100%; display:flex; justify-content:space-between; padding:20px 50px; background:rgba(0,0,0,0.3); position:fixed; top:0; font-family:'Pacifico', cursive; box-sizing: border-box; }  
.center { position:absolute; top:55%; left:50%; transform:translate(-50%,-50%); width:80%; text-align:center; }  
#task { font-size:32px; line-height:2; color:#888; }  
.correct {color: var(--accent);}  
.wrong {color:#ff4d4d;}  
#hiddenInput { opacity:0; position:absolute; }  
#timer { font-size:28px; color: var(--primary); text-shadow:0 0 10px var(--primary); margin-bottom:15px; }  
.btn { margin:10px; padding:12px 30px; border:none; border-radius:10px; background: var(--primary); color:white; font-size:16px; cursor:pointer; }  

#finishOverlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); display: none; justify-content: center; align-items: center; flex-direction: column; z-index: 200000; }
#finishOverlay h1 { font-family: 'Pacifico', cursive; color: var(--primary); font-size: 60px; }
</style>  </head>  <body onclick="focusInput(); unlockAudio();">  

<div id="finishOverlay">
    <h1>Congratulations! 🚀</h1>
    <div id="finalScore" style="font-size:28px; margin:20px 0;"></div>
    <div style="display:flex; gap:10px;">
        <button class="btn" onclick="nextLevel()">Next Level</button>
        <button class="btn" style="background:gray;" onclick="restartTest()">Restart</button>
    </div>
</div>

<div class="left-menu">  
<button onclick="showTest()">Test</button>  
<button onclick="openLogin()">Login</button>  
<button onclick="openCreate()">Create Account</button>  
<button onclick="openAdmin()" style="background:#ff4d4d;">ADMIN PANEL</button>
</div>  

<div class="modal" id="adminPanel" onclick="event.stopPropagation()">
    <h2 style="color:var(--primary)">Admin Settings & Stats</h2>
    
    <div style="background:rgba(255,255,255,0.1); padding:15px; border-radius:10px; margin-bottom:15px;">
        <label>Change Theme:</label>
        <select id="themeSelect" onchange="changeTheme()">
            <option value="default">Midnight Dark (Default)</option>
            <option value="light-theme">Arctic White</option>
            <option value="neon-theme">Neon Party</option>
            <option value="matrix-theme">The Matrix</option>
        </select>

        <label>Typing Sound:</label>
        <select id="audioSelect">
            <option value="classic">Classic Beep</option>
            <option value="mechanical">Mechanical Keyboard</option>
            <option value="wood">Wooden Click</option>
            <option value="none">Silent</option>
        </select>
    </div>

    <div id="statsTable"></div>
    <br>
    <button class="btn" onclick="closeAll()">Close Dashboard</button>
</div>

<div class="modal" id="loginBox" onclick="event.stopPropagation()">  
<h3>Login</h3>  
<input type="text" id="username" placeholder="Username">  
<input type="password" id="password" placeholder="Password">  
<button class="btn" onclick="login()">Login</button>  
<button class="btn" style="background:gray" onclick="closeAll()">Close</button>
</div>  

<div class="modal" id="createBox" onclick="event.stopPropagation()">  
<h3>Create Account</h3>  
<input type="text" id="newUsername" placeholder="Username">  
<input type="password" id="newPassword" placeholder="Password">  
<button class="btn" onclick="createAccount()">Create</button>  
<button class="btn" style="background:gray" onclick="closeAll()">Close</button>
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
<div id="timer">⏱ 60 sec</div>  
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
<button class="btn" onclick="startTest(60)">1 Min</button>  
<button class="btn" onclick="startTest(180)">3 Min</button>  
<button class="btn" onclick="startTest(300)">5 Min</button>  
</div>  

<script>  
let currentUser = null;  
let currentLevelIndex = 0;
let isPaused = false;
let testRunning = false;
let audioCtx, timer, timeLeft=60, startTime, totalTyped=0;

const typingLevels = [
    "Technology is evolving rapidly in today's world.",
    "Efficient typing skills are essential for productivity in the modern digital era.",
    "The quick brown fox jumps over the lazy dog while the sun sets behind the hills.",
    "Quantum computing uses phenomena such as superposition and entanglement.",
    "Innovation distinguishes between a leader and a follower."
];

function closeAll(){  
    loginBox.style.display="none"; createBox.style.display="none";  
    adminPanel.style.display="none"; finishOverlay.style.display="none";
    testBox.style.display="none";
}  

function changeTheme() {
    let theme = document.getElementById("themeSelect").value;
    document.body.className = theme === "default" ? "" : theme;
}

// Sound Logic
function playKeySound(){  
    let type = document.getElementById("audioSelect").value;
    if(type === "none" || !audioCtx) return;  
    let osc = audioCtx.createOscillator();  
    let gain = audioCtx.createGain();  
    
    if(type === "mechanical") { osc.type = "square"; osc.frequency.value = 150; gain.gain.value = 0.02; }
    else if(type === "wood") { osc.type = "sine"; osc.frequency.value = 400; gain.gain.value = 0.05; }
    else { osc.type = "triangle"; osc.frequency.value = 250; gain.gain.value = 0.05; }

    osc.connect(gain); gain.connect(audioCtx.destination);  
    osc.start(); osc.stop(audioCtx.currentTime + 0.05);  
}  

async function login(){  
    let u = document.getElementById("username").value, p = document.getElementById("password").value;  
    const res = await fetch('/api/login', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({u, p})});
    if(res.ok){ currentUser = u; document.getElementById("userDisplay").innerHTML = "👤 "+u; closeAll(); } 
    else alert("Wrong Login!");  
}  

async function openAdmin(){
    stopTyping(); closeAll();
    document.getElementById("adminPanel").style.display = "block";
    const res = await fetch('/api/admin_data');
    const userStats = await res.json();
    let sortedUsers = Object.keys(userStats).sort((a,b) => userStats[b].bestWpm - userStats[a].bestWpm);
    let html = "<table><tr><th>Rank</th><th>User</th><th>WPM</th></tr>";
    sortedUsers.forEach((name, index) => { html += `<tr><td>#${index+1}</td><td>${name}</td><td>${userStats[name].bestWpm}</td></tr>`; });
    document.getElementById("statsTable").innerHTML = html + "</table>";
}

function stopTyping(){ clearInterval(timer); isPaused = true; }  

window.addEventListener("keydown", (e) => {
    if(e.code === "Space" && isPaused && testRunning) { isPaused = false; timer = setInterval(updateTimer, 1000); }
    if(e.code === "Enter" && testRunning) finishTest();
});

function loadText(){  
    closeAll(); document.getElementById("gameButtons").style.display="none";  
    currentText = typingLevels[currentLevelIndex % typingLevels.length]; 
    let html=""; for(let i=0;i<currentText.length;i++){ html+="<span>"+currentText[i]+"</span>"; }  
    task.innerHTML=html; hiddenInput.value=""; startTime = new Date().getTime();  
    isPaused = false; testRunning = true; clearInterval(timer); timer = setInterval(updateTimer, 1000);  
}  

function updateTimer(){ if(!isPaused){ timeLeft--; document.getElementById("timer").innerText="⏱ "+timeLeft+" sec"; if(timeLeft<=0) finishTest(); } }  

hiddenInput.addEventListener("input", function() {  
    if(isPaused || !testRunning) return;
    playKeySound();  
    let input=this.value, spans=document.querySelectorAll("#task span"); totalTyped=input.length;  
    for(let i=0;i<spans.length;i++){  
        if(input[i]==null) spans[i].className = "";  
        else spans[i].className = (input[i]===currentText[i]) ? "correct" : "wrong";  
    }  
    if(input===currentText) finishTest();  
});  

async function finishTest(){  
    clearInterval(timer); testRunning = false;
    let timeUsed = (new Date().getTime() - startTime) / 60000;  
    let wpm = Math.round((totalTyped/5)/timeUsed) || 0;  
    let acc = Math.round((document.querySelectorAll(".correct").length / totalTyped) * 100) || 0;
    document.getElementById("finalScore").innerText = wpm + " WPM | " + acc + "% Acc";
    document.getElementById("finishOverlay").style.display = "flex";
    if(currentUser) await fetch('/api/update_stats', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({u: currentUser, wpm: wpm, acc: acc})});
}  

function nextLevel() { currentLevelIndex++; timeLeft=60; loadText(); }
function restartTest() { timeLeft=60; loadText(); }
function showTest(){ closeAll(); document.getElementById("testBox").style.display="block"; }  
function startTest(t){ timeLeft=t; loadText(); }  
function startSite(){ welcomeScreen.style.display="none"; loadText(); }  
function focusInput(){ document.getElementById("hiddenInput").focus(); }
function unlockAudio(){ if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)(); }
</script>  
</body>  
</html>  
"""

if __name__ == "__main__":
    app.run(debug=True)
