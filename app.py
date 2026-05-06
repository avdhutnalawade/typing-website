from flask import Flask, request, jsonify, render_template_string
import json
import os

app = Flask(__name__)

# --- BACKEND STORAGE (database.json) ---
DB_FILE = 'database.json'

def load_db():
    if not os.path.exists(DB_FILE):
        data = {"users": {"admin": "1234"}, "userStats": {"admin": {"attempts": 0, "bestWpm": 0, "accuracy": 0, "level": 1}}}
        save_db(data)
        return data
    with open(DB_FILE, 'r') as f: return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f, indent=4)

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    db = load_db()
    u, p = data.get('u'), data.get('p')
    if db['users'].get(u) == p:
        return jsonify({"status": "success", "stats": db['userStats'].get(u, {})})
    return jsonify({"status": "fail"}), 401

@app.route('/api/create', methods=['POST'])
def create():
    data = request.json
    db = load_db()
    u, p = data.get('u'), data.get('p')
    if u in db['users']: return jsonify({"status": "exists"}), 400
    db['users'][u] = p
    db['userStats'][u] = {"attempts": 0, "bestWpm": 0, "accuracy": 0, "level": 1}
    save_db(db)
    return jsonify({"status": "success"})

@app.route('/api/update', methods=['POST'])
def update_stats():
    data = request.json
    db = load_db()
    u = data.get('u')
    if u in db['userStats']:
        s = db['userStats'][u]
        s['attempts'] += 1
        if data.get('wpm') > s['bestWpm']: s['bestWpm'] = data.get('wpm')
        s['accuracy'] = data.get('acc')
        
        # Level Logic
        old_lvl = s.get('level', 1)
        if s['bestWpm'] > 45: s['level'] = 3
        elif s['bestWpm'] > 25: s['level'] = 2
        else: s['level'] = 1
        
        save_db(db)
        return jsonify({"levelUp": s['level'] > old_lvl, "newLevel": s['level']})
    return jsonify({"status": "error"})

@app.route('/api/admin')
def get_admin():
    return jsonify(load_db()['userStats'])

# --- UI CODE (HTML/CSS/JS) ---
HTML_CODE = """
<!DOCTYPE html><html><head><title>Pro Typing Level System</title>
<link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@500&family=Pacifico&display=swap" rel="stylesheet">
<style>
body { margin:0; font-family:'Roboto Mono', monospace; background:#1a1a2e; color:white; overflow:hidden; }
.left-menu{ position:fixed; top:120px; left:20px; display:flex; flex-direction:column; gap:10px; z-index:1000; }
.left-menu button{ padding:10px; border:none; border-radius:6px; background:#00c6ff; color:white; cursor:pointer; font-weight:bold; }

/* FULL SCREEN PROGRESS MESSAGE */
#levelOverlay {
    position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.95);
    display:none; flex-direction:column; justify-content:center; align-items:center; z-index:20000; text-align:center;
}
.lvl-box { padding:40px; border-radius:20px; border:3px solid #00ffff; box-shadow:0 0 30px #00ffff; }

.modal{ position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); background:#0a0a1e; padding:30px; border-radius:15px; display:none; z-index:9999; border:2px solid #00c6ff; min-width:400px; }
input{ width:100%; margin:10px 0; padding:10px; border-radius:5px; border:none; box-sizing:border-box; }
.header { width:100%; display:flex; justify-content:space-between; padding:20px 50px; background:rgba(0,0,0,0.3); position:fixed; top:0; box-sizing:border-box; }
.center { position:absolute; top:55%; left:50%; transform:translate(-50%,-50%); width:80%; text-align:center; }
#task { font-size:30px; color:#aaa; line-height:1.6; }
.correct { color:#00ff88; }
.wrong { color:#ff4d4d; text-decoration:underline; }
#hiddenInput { opacity:0; position:absolute; }
#timer { font-size:28px; color:#00ffff; margin-bottom:10px; }
.btn { padding:12px 25px; border:none; border-radius:10px; background:linear-gradient(45deg,#00c6ff,#0072ff); color:white; cursor:pointer; font-size:16px; margin:5px; }
table { width: 100%; border-collapse: collapse; color: white; }
th, td { border: 1px solid #333; padding: 10px; text-align: center; }
#levelTag { background:#ff4d4d; padding:5px 12px; border-radius:12px; font-size:14px; margin-left:10px; }
</style></head>
<body onclick="document.getElementById('hiddenInput').focus(); unlockAudio();">

<div id="levelOverlay">
    <div class="lvl-box">
        <h1 style="font-family:'Pacifico'; color:#00ffff; font-size:50px;">LEVEL UP! 🚀</h1>
        <h2 id="lvlMsg">Training Progress: Level 2 reached</h2>
        <button class="btn" onclick="document.getElementById('levelOverlay').style.display='none'; nextTest();">Continue Training</button>
    </div>
</div>

<div class="left-menu">
    <button onclick="showTest()">Test</button>
    <button onclick="openLogin()">Login</button>
    <button onclick="openCreate()">Create Account</button>
    <button onclick="openAdmin()" style="background:#ff4d4d;">LEADERBOARD</button>
</div>

<div class="header">
    <h2 style="font-family:'Pacifico'; color:#00ffff; margin:0;">Typing Master</h2>
    <div id="userDisplay"></div>
</div>

<div class="center">
    <div id="timer">⏱ 60 sec</div>
    <div id="task">Please login to track your progress level.</div>
    <input id="hiddenInput" autocomplete="off">
    <div id="result" style="font-size:22px; margin:20px;"></div>
    <div>
        <button class="btn" id="nextBtn" style="display:none;" onclick="nextTest()">Next</button>
        <button class="btn" id="restartBtn" style="display:none;" onclick="nextTest()">Restart</button>
    </div>
</div>

<div class="modal" id="loginBox">
    <h3>User Login</h3>
    <input type="text" id="u" placeholder="Username">
    <input type="password" id="p" placeholder="Password">
    <button class="btn" onclick="login()">Login</button>
    <button class="btn" style="background:gray" onclick="closeAll()">Close</button>
</div>

<div class="modal" id="adminPanel">
    <h2 style="color:#00ffff">Global Rankings</h2>
    <div id="statsTable" style="max-height:300px; overflow-y:auto;"></div>
    <button class="btn" onclick="closeAll()">Close</button>
</div>

<div class="modal" id="testBox">
    <h3>Select Time</h3>
    <button class="btn" onclick="startTest(60)">1 Min</button>
    <button class="btn" onclick="startTest(180)">3 Min</button>
</div>

<script>
let currentUser = null, currentLevel = 1, timer, timeLeft=60, startTime, totalTyped=0;
const levels = {
    1: ["The sun is very bright.", "I like to type fast.", "Cats are cute animals."],
    2: ["Technology is changing the world very rapidly every day.", "Consistent practice is the key to mastering any skill."],
    3: ["Sophisticated artificial intelligence requires complex algorithms and data structures to function properly."]
};

function closeAll() { document.querySelectorAll('.modal').forEach(m=>m.style.display='none'); }
function openLogin() { closeAll(); document.getElementById('loginBox').style.display='block'; }
function showTest() { closeAll(); document.getElementById('testBox').style.display='block'; }

async function login(){
    let u = document.getElementById('u').value, p = document.getElementById('p').value;
    const res = await fetch('/api/login', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({u,p})});
    if(res.ok){
        const data = await res.json();
        currentUser = u; currentLevel = data.stats.level || 1;
        updateHeader(); closeAll(); nextTest();
    } else alert("Invalid Credential");
}

async function openCreate(){
    let u = prompt("Username:"), p = prompt("Password:");
    if(u&&p) await fetch('/api/create', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({u,p})});
}

function updateHeader(){
    document.getElementById('userDisplay').innerHTML = `<span style="background:#00c6ff; padding:5px 10px; border-radius:10px;">👤 ${currentUser}</span> <span id="levelTag">Lvl ${currentLevel}</span>`;
}

function nextTest(){
    document.getElementById('result').innerText = "";
    document.getElementById('nextBtn').style.display = "none";
    let pool = levels[currentLevel] || levels[1];
    currentText = pool[Math.floor(Math.random()*pool.length)];
    let html = ""; for(let c of currentText) html += `<span>${c}</span>`;
    document.getElementById('task').innerHTML = html;
    document.getElementById('hiddenInput').value = "";
    startTime = new Date().getTime();
    clearInterval(timer); timer = setInterval(updateTimer, 1000);
}

function updateTimer(){
    timeLeft--; document.getElementById('timer').innerText = `⏱ ${timeLeft} sec`;
    if(timeLeft<=0) finishTest();
}

document.getElementById('hiddenInput').addEventListener('input', function(){
    let val = this.value, spans = document.querySelectorAll('#task span');
    totalTyped = val.length;
    spans.forEach((s, i) => {
        if(!val[i]) s.className = "";
        else if(val[i]===currentText[i]) s.className = "correct";
        else s.className = "wrong";
    });
    if(val === currentText) finishTest();
});

async function finishTest(){
    clearInterval(timer);
    let wpm = Math.round((totalTyped/5)/((new Date().getTime()-startTime)/60000)) || 0;
    let acc = Math.round((document.querySelectorAll('.correct').length/totalTyped)*100) || 0;
    document.getElementById('result').innerText = `WPM: ${wpm} | Accuracy: ${acc}%`;
    document.getElementById('nextBtn').style.display = "inline-block";
    
    if(currentUser){
        const res = await fetch('/api/update', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({u:currentUser, wpm, acc})});
        const data = await res.json();
        if(data.levelUp){
            currentLevel = data.newLevel; updateHeader();
            document.getElementById('lvlMsg').innerText = `Progress Saved: You reached Level ${currentLevel}`;
            document.getElementById('levelOverlay').style.display = 'flex';
        }
    }
}

async function openAdmin(){
    closeAll(); document.getElementById('adminPanel').style.display='block';
    const res = await fetch('/api/admin');
    const data = await res.json();
    let html = "<table><tr><th>User</th><th>Lvl</th><th>WPM</th></tr>";
    for(let u in data) html += `<tr><td>${u}</td><td>${data[u].level}</td><td>${data[u].bestWpm}</td></tr>`;
    document.getElementById('statsTable').innerHTML = html + "</table>";
}

function startTest(t) { timeLeft = t; closeAll(); nextTest(); }
let audioCtx; function unlockAudio(){ if(!audioCtx) audioCtx = new AudioContext(); }
</script></body></html>
"""

if __name__ == "__main__":
    app.run(debug=True)
