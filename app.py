from flask import Flask, request, jsonify, render_template_string
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# --- BACKEND DATABASE LOGIC ---
DB_FILE = 'database.json'

def load_data():
    if not os.path.exists(DB_FILE):
        initial_data = {
            "users": {"admin": "1234"},
            "userStats": {"admin": {"attempts": 0, "bestWpm": 0, "accuracy": 0, "history": []}}
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
        
        # तारीख आणि वेळेसह इतिहास एंट्री तयार करणे
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

# --- HTML / CSS / JAVASCRIPT CODE ---
HTML_CODE = """
<!DOCTYPE html>  <html>  
<head>  
<title>Beginner Typing Speed Test</title>  
<link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@500&family=Pacifico&display=swap" rel="stylesheet">  
<style>  
:root { --bg: #1a1a2e; --text: white; --primary: #00c6ff; }
body { margin:0; font-family:'Roboto Mono', monospace; background: var(--bg); color: var(--text); overflow:hidden; transition: 0.3s; }  
body.light-theme { --bg: #f0f2f5; --text: #1a1a2e; --primary: #0072ff; }
body.neon-theme { --bg: #000; --text: #0f0; --primary: #f0f; }
body.matrix-theme { --bg: #000; --text: #00ff41; --primary: #003b00; }
.left-menu{ position:fixed; top:120px; left:20px; display:flex; flex-direction:column; gap:10px; z-index:10000; }  
.left-menu button{ padding:10px; border:none; border-radius:6px; background: var(--primary); color: white; cursor:pointer; font-weight: bold; width: 150px; text-align: left;}  
.modal{ position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); background:rgba(10, 10, 30, 0.98); padding:30px; border-radius:15px; display:none; z-index:99999; min-width: 400px; max-width: 600px; border: 2px solid var(--primary); box-shadow: 0 0 30px rgba(0, 198, 255, 0.3); max-height: 80vh; overflow-y: auto;}  
.modal input, .modal select { width:100%; margin:10px 0; padding:10px; border:none; border-radius:5px; box-sizing: border-box; background: #222; color: white; }  
.step-item { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #28a745; text-align: left; }
.video-frame { width: 100%; height: 250px; border-radius: 8px; margin-top: 10px; }
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
#finishOverlay {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(10, 10, 30, 0.95);
    display: none; justify-content: center; align-items: center;
    flex-direction: column; z-index: 200000; text-align: center;
}
#finishOverlay h1 { font-family: 'Pacifico', cursive; color: #00ffff; font-size: 60px; margin: 0; }
#finalScore { font-size: 28px; color: #00ff88; margin: 20px 0; }

/* फिल्टर बटन्स डिझाईन */
.filter-btn-container { display: flex; gap: 10px; margin-bottom: 15px; }
.filter-btn { background: #222; color: white; border: 1px solid var(--primary); padding: 5px 15px; border-radius: 5px; cursor: pointer; font-family: inherit; }
.filter-btn.active { background: var(--primary); color: black; font-weight: bold; }
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
<button onclick="showTest()">Test</button>  
<button onclick="openLogin()">Login</button>  
<button onclick="openCreate()">Create Account</button>  
<button onclick="openAdmin()" style="background:#ff4d4d;">ADMIN PANEL</button>
<button onclick="openSettings()" style="background:#ffa500;">SETTINGS ⚙️</button>
<button onclick="openLearn()" style="background:#28a745;">LEARN 🎓</button>
</div>  

<div class="modal" id="learnBox" onclick="event.stopPropagation()">
    <h2 style="color: #28a745">Learn Typing</h2>
    <div class="step-item">
        <h3>Step 1: Proper Positioning</h3>
        <iframe class="video-frame" src="https://www.youtube.com/embed/1ArVtCQqQRE" frameborder="0" allowfullscreen></iframe>
    </div>
    <div class="step-item">
        <h3>Step 2: Pro Techniques</h3>
        <iframe class="video-frame" src="https://www.youtube.com/embed/EMUH9BPmqcY" frameborder="0" allowfullscreen></iframe>
    </div>
    <button class="btn" onclick="closeAll()">Close</button>
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

<div class="modal" id="adminPanel" onclick="event.stopPropagation()">
    <h2 style="color:#00ffff">Admin Leaderboard</h2>
    <div class="filter-btn-container">
        <button class="filter-btn active" id="btnAll" onclick="filterAdminData('all')">All Time</button>
        <button class="filter-btn" id="btn1" onclick="filterAdminData(1)">1 Day</button>
        <button class="filter-btn" id="btn30" onclick="filterAdminData(30)">1 Month</button>
        <button class="filter-btn" id="btn365" onclick="filterAdminData(365)">1 Year</button>
    </div>
    <div id="statsTable"></div>
    <br>
    <button class="btn" onclick="closeAll()">Close Dashboard</button>
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

<div class="test-box" id="testBox" style="display:none; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); background:rgba(255,255,255,0.1); padding:25px; border-radius:15px; text-align:center;">  
<h2>Select Time</h2>  
<button onclick="startTest(60)">1 Min</button>  
<button onclick="startTest(180)">3 Min</button>  
<button onclick="startTest(300)">5 Min</button>  
<button onclick="startTest(600)">10 Min</button>  
</div>  

<script>  
let currentUser = null;  
let currentLevelIndex = 0;
let isPaused = false;
let testRunning = false;
let audioCtx;
let timer, timeLeft=60;  
let startTime,totalTyped=0;  
let currentText = "";
let globalUserStats = {}; // डेटाबेस सेव्ह करण्यासाठी ग्लोबल व्हेरिएबल

const typingLevels = [
    "Technology is evolving rapidly in today's world.",
    "Efficient typing skills are essential for productivity in the modern digital era.",
    "The quick brown fox jumps over the lazy dog while the sun sets behind the green hills.",
    "Quantum computing uses quantum-mechanical phenomena such as superposition and entanglement.",
    "Complex systems require a profound understanding of architecture and design patterns to succeed."
];

function closeAll(){  
    loginBox.style.display="none";  
    createBox.style.display="none";  
    settingsBox.style.display="none";
    learnBox.style.display="none";
    if(document.getElementById("testBox")) document.getElementById("testBox").style.display="none";  
    adminPanel.style.display="none";
    finishOverlay.style.display="none";
}  

function openLearn() { stopTyping(); closeAll(); learnBox.style.display="block"; }
function openSettings() { stopTyping(); closeAll(); settingsBox.style.display="block"; }
function changeTheme() { document.body.className = document.getElementById("themeSelect").value; }
function openLogin(){ stopTyping(); closeAll(); loginBox.style.display="block"; username.focus(); }  

async function login(){  
    let u = document.getElementById("username").value;  
    let p = document.getElementById("password").value;  
    const res = await fetch('/api/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({u, p})
    });
    if(res.ok){  
        currentUser = u;  
        document.getElementById("userDisplay").innerHTML = "<span class='user-circle'>👤 "+u+"</span> <button onclick='logout()' style='background:none; border:1px solid #ff4d4d; color:#ff4d4d; border-radius:5px; margin-left:10px; cursor:pointer;'>Logout</button>";  
        alert("Login Successful!");  
        closeAll();  
    } else{ alert("Wrong Username or Password"); }  
}  

function openCreate(){ stopTyping(); closeAll(); createBox.style.display="block"; newUsername.focus(); }  

async function createAccount(){  
    let u = document.getElementById("newUsername").value;  
    let p = document.getElementById("newPassword").value;  
    if(u && p){  
        const res = await fetch('/api/create', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({u, p})
        });
        if(res.ok){ alert("Account Created for " + u); closeAll(); } 
        else { alert("User already exists or error!"); }
    } else{ alert("Enter Username & Password"); }  
}  

function logout(){ currentUser = null; document.getElementById("userDisplay").innerHTML = ""; }  

async function openAdmin(){
    stopTyping();
    closeAll();
    document.getElementById("adminPanel").style.display = "block";
    const res = await fetch('/api/admin_data');
    globalUserStats = await res.json();
    filterAdminData('all');
}

// फ्रंटएंडवर दिवसानुसार फिल्टर मोजणारे फंक्शन
function filterAdminData(days) {
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    if(days === 'all') document.getElementById('btnAll').classList.add('active');
    else if(days === 1) document.getElementById('btn1').classList.add('active');
    else if(days === 30) document.getElementById('btn30').classList.add('active');
    else if(days === 365) document.getElementById('btn365').classList.add('active');

    let processedStats = {};
    let now = new Date();

    Object.keys(globalUserStats).forEach(name => {
        let user = globalUserStats[name];
        
        if (!user.history || days === 'all') {
            processedStats[name] = {
                attempts: user.attempts,
                bestWpm: user.bestWpm,
                accuracy: user.accuracy
            };
            return;
        }

        let filteredAttempts = 0;
        let filteredBestWpm = 0;
        let filteredAcc = 0;

        user.history.forEach(entry => {
            let entryDate = new Date(entry.date_time.replace(' ', 'T'));
            let timeDiff = now - entryDate;
            let daysDiff = timeDiff / (1000 * 60 * 60 * 24);

            if (daysDiff <= days) {
                filteredAttempts++;
                if (entry.wpm > filteredBestWpm) filteredBestWpm = entry.wpm;
                filteredAcc = entry.accuracy;
            }
        });

        processedStats[name] = {
            attempts: filteredAttempts,
            bestWpm: filteredBestWpm,
            accuracy: filteredAcc
        };
    });

    let sortedUsers = Object.keys(processedStats).sort((a,b) => processedStats[b].bestWpm - processedStats[a].bestWpm);
    let html = "<table><tr><th>Rank</th><th>User</th><th>Tests</th><th>Max WPM</th><th>Accuracy</th></tr>";
    sortedUsers.forEach((name, index) => {
        let s = processedStats[name];
        html += `<tr><td>#${index + 1}</td><td>${name}</td><td>${s.attempts}</td><td>${s.bestWpm}</td><td>${s.accuracy}%</td></tr>`;
    });
    html += "</table>";
    document.getElementById("statsTable").innerHTML = html;
}

function stopTyping(){ 
    clearInterval(timer); 
    isPaused = true;
    document.getElementById("hiddenInput").blur(); 
}  

function resumeTyping(){
    if(isPaused && timeLeft > 0 && testRunning){
        isPaused = false;
        clearInterval(timer);
        timer = setInterval(updateTimer, 1000);
        document.getElementById("hiddenInput").focus();
    }
}

window.addEventListener("keydown", function(e) {
    if(e.code === "Space" && isPaused && finishOverlay.style.display !== "flex" && testRunning) {
        resumeTyping();
        e.preventDefault();
    }
    if(e.code === "Enter" && testRunning) {
        finishTest();
    }
});

function unlockAudio(){ if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)(); }  
function playKeySound(){  
    let type = document.getElementById("audioSelect").value;
    if(type === "silent" || !audioCtx) return;  
    let osc = audioCtx.createOscillator();  
    let gain = audioCtx.createGain();  
    if(type === "mechanical") {
        osc.type = "sawtooth";
        osc.frequency.value = 150 + Math.random()*50;
        gain.gain.value = 0.02;
    } else {
        osc.type = "square";
        osc.frequency.value = 200 + Math.random()*100;
        gain.gain.value = 0.05;
    }
    osc.connect(gain); gain.connect(audioCtx.destination);  
    osc.start(); osc.stop(audioCtx.currentTime + 0.05);  
}  

function loadText(){  
    closeAll();
    result.innerHTML=""; 
    document.getElementById("gameButtons").style.display="none";  
    currentText = typingLevels[currentLevelIndex % typingLevels.length]; 
    let html="";  
    for(let i=0;i<currentText.length;i++){ html+="<span>"+currentText[i]+"</span>"; }  
    task.innerHTML=html; hiddenInput.value=""; 
    startTime = new Date().getTime();  
    isPaused = false;
    testRunning = true;
    clearInterval(timer); 
    timer = setInterval(updateTimer, 1000);  
}  

function updateTimer(){  
    if(!isPaused){
        timeLeft--; 
        document.getElementById("timer").innerText="⏱ "+timeLeft+" sec";  
        if(timeLeft<=0) finishTest();  
    }
}  

function focusInput(){ if(!isPaused && testRunning) document.getElementById("hiddenInput").focus(); }  

hiddenInput.addEventListener("input",function(){  
    if(isPaused || !testRunning) return;
    playKeySound();  
    let input=this.value;  
    let spans=document.querySelectorAll("#task span");  
    totalTyped=input.length;  
    for(let i=0;i<spans.length;i++){  
        if(input[i]==null) spans[i].classList.remove("correct","wrong");  
        else if(input[i]===currentText[i]){ spans[i].classList.add("correct"); spans[i].classList.remove("wrong"); }  
        else { spans[i].classList.add("wrong"); spans[i].classList.remove("correct"); }  
    }  
    if(input===currentText) finishTest();  
});  

async function finishTest(){  
    clearInterval(timer);  
    isPaused = true;
    testRunning = false;
    let timeUsed = (new Date().getTime() - startTime) / 60000;  
    let wpm = Math.round((totalTyped/5)/timeUsed) || 0;  
    let correctChars = document.querySelectorAll(".correct").length;
    let acc = totalTyped > 0 ? Math.round((correctChars / totalTyped) * 100) : 0;

    document.getElementById("finalScore").innerText = "Speed: " + wpm + " WPM | Accuracy: " + acc + "%";
    document.getElementById("finishOverlay").style.display = "flex";

    if(currentUser) {
        await fetch('/api/update_stats', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({u: currentUser, wpm: wpm, acc: acc})
        });
    }
}  

function nextLevel() { currentLevelIndex++; timeLeft = 60; loadText(); }
function restartTest() { timeLeft = 60; loadText(); }
function showTest(){ stopTyping(); closeAll(); document.getElementById("testBox").style.display="block"; }  
function startTest(t){ timeLeft=t; document.getElementById("testBox").style.display="none"; loadText(); }  
function startSite(){ welcomeScreen.style.display="none"; loadText(); }  
</script>  
</body>  
</html>  
"""

if __name__ == "__main__":
    app.run(debug=True)
