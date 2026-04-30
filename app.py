from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<title>Beginner Typing Speed Test</title>

<link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@500&family=Pacifico&display=swap" rel="stylesheet">

<!-- 🎆 ADDED -->
<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>

<style>
body {
    margin:0;
    font-family:'Roboto Mono', monospace;
    background:#1a1a2e;
    color:white;
    overflow:hidden;
}

/* 🔥 LEFT BUTTONS (ADDED) */
.left-menu{
    position:fixed;
    top:120px;
    left:20px;
    display:flex;
    flex-direction:column;
    gap:10px;
    z-index:9999;
}
.left-menu button{
    padding:10px;
    border:none;
    border-radius:6px;
    background:#00c6ff;
    cursor:pointer;
}

/* 🔥 MODAL CENTER (ADDED) */
.modal{
    position:fixed;
    top:50%;
    left:50%;
    transform:translate(-50%,-50%);
    background:rgba(0,0,0,0.9);
    padding:20px;
    border-radius:10px;
    display:none;
    z-index:9999;
}
.modal input{
    width:100%;
    margin:8px 0;
    padding:8px;
    border:none;
    border-radius:5px;
}

/* 🔥 USER CIRCLE (ADDED) */
.user-circle{
    background:#00c6ff;
    padding:8px 15px;
    border-radius:20px;
}

/* 🎉 POPUP (ADDED) */
.popup-msg{
    position:fixed;
    top:20%;
    left:50%;
    transform:translateX(-50%);
    background:#00ff88;
    color:black;
    padding:10px 20px;
    border-radius:10px;
    font-weight:bold;
    animation:fade 2s ease;
    z-index:9999;
}

@keyframes fade{
    0%{opacity:0; transform:translate(-50%,-20px);}
    50%{opacity:1;}
    100%{opacity:0; transform:translate(-50%,0);}
}

/* 🔥 ORIGINAL CSS SAME */
#welcomeScreen{
    position:fixed;
    top:0;
    left:0;
    width:100%;
    height:100%;
    background:linear-gradient(135deg,#000428,#004e92);
    display:flex;
    justify-content:center;
    align-items:center;
    flex-direction:column;
    z-index:99999;
}

#welcomeText{
    font-size:45px;
    font-family:'Pacifico', cursive;
    color:#00ffff;
    text-shadow:0 0 20px #00ffff;
}

.start-btn{
    margin-top:20px;
    padding:12px 25px;
    border:none;
    border-radius:10px;
    background:linear-gradient(45deg,#00c6ff,#0072ff);
    color:white;
    cursor:pointer;
    font-size:16px;
}

.header {
    width:100%;
    display:flex;
    justify-content:space-between;
    padding:20px 50px;
    background:rgba(0,0,0,0.3);
    position:fixed;
    top:0;
    font-family:'Pacifico', cursive;
}
.header h2{color:#00ffff;}

.center {
    position:absolute;
    top:55%;
    left:50%;
    transform:translate(-50%,-50%);
    width:80%;
    text-align:center;
}

#task {
    font-size:32px;
    line-height:2;
    color:#aaa;
}

.correct {color:#00ff88;}
.wrong {color:#ff4d4d;}

#hiddenInput {
    opacity:0;
    position:absolute;
}

#timer {
    font-size:28px;
    color:#00ffcc;
    text-shadow:0 0 10px #00ffff;
    margin-bottom:15px;
}

.btn {
    margin:15px;
    padding:12px 30px;
    border:none;
    border-radius:10px;
    background:linear-gradient(45deg,#00c6ff,#0072ff);
    color:white;
    font-size:16px;
    cursor:pointer;
}

/* 🔥 TEST CENTER (ONLY POSITION CHANGE) */
.test-box {
    position:fixed;
    top:50%;
    left:50%;
    transform:translate(-50%,-50%);
    display:none;
    text-align:center;
    background:rgba(255,255,255,0.1);
    padding:25px;
    border-radius:15px;
}
</style>
</head>

<body onclick="focusInput(); unlockAudio();">

<!-- 🔥 LEFT MENU (ADDED) -->
<div class="left-menu">
<button onclick="showTest()">Test</button>
<button onclick="openLogin()">Login</button>
<button onclick="openCreate()">Create Account</button>
</div>

<!-- 🔥 LOGIN -->
<div class="modal" id="loginBox" onclick="event.stopPropagation()">
<h3>Login</h3>
<input type="text" id="username" placeholder="Username">
<input type="password" id="password" placeholder="Password">
<button onclick="login()">Login</button>
</div>

<!-- 🔥 CREATE ACCOUNT -->
<div class="modal" id="createBox" onclick="event.stopPropagation()">
<h3>Create Account</h3>
<input type="text" id="newUsername" placeholder="Username">
<input type="password" id="newPassword" placeholder="Password">
<button onclick="createAccount()">Create</button>
</div>

<!-- 🔥 ORIGINAL WELCOME -->
<div id="welcomeScreen">
    <div id="welcomeText">Welcome 🚀</div>
    <button class="start-btn" onclick="startSite()">Start</button>
</div>

<div class="header">
<h2>Welcome to Beginner Typing Speed Test</h2>
<div id="userDisplay"></div>
</div>

<div class="center">
<div id="timer"></div>
<div id="task"></div>
<input id="hiddenInput">
<div id="result"></div>

<div>
<button class="btn" onclick="nextTest()" id="nextBtn" style="display:none;">Next</button>
<button class="btn" onclick="restartTest()" id="restartBtn" style="display:none;">Restart</button>
</div>
</div>

<div class="test-box" id="testBox">
<h2>Select Time</h2>
<button onclick="startTest(60)">1 Min</button>
<button onclick="startTest(180)">3 Min</button>
<button onclick="startTest(300)">5 Min</button>
<button onclick="startTest(600)">10 Min</button>
</div>

<script>

/* USERS */
let users = {"admin":"1234"};
let currentUser = null;

/* BEST SCORE (ADDED) */
let bestWPM = 0;

/* CLOSE ALL */
function closeAll(){
    loginBox.style.display="none";
    createBox.style.display="none";
    testBox.style.display="none";
}

/* LOGIN */
function openLogin(){
    stopTyping();
    closeAll();
    loginBox.style.display="block";
}

function login(){
    let u=username.value;
    let p=password.value;

    if(users[u] && users[u]==p){
        currentUser=u;
        userDisplay.innerHTML="<span class='user-circle'>👤 "+u+"</span> <button onclick='logout()'>Logout</button>";
        closeAll();
    }
}

/* CREATE */
function openCreate(){
    stopTyping();
    closeAll();
    createBox.style.display="block";
}

function createAccount(){
    users[newUsername.value]=newPassword.value;
    closeAll();
}

/* LOGOUT */
function logout(){
    currentUser=null;
    userDisplay.innerHTML="";
}

/* AUDIO */
let audioCtx;
function unlockAudio(){
    if(!audioCtx){
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
}

/* POPUP (ADDED) */
function showPopup(msg){
    let div=document.createElement("div");
    div.className="popup-msg";
    div.innerText=msg;
    document.body.appendChild(div);
    setTimeout(()=>div.remove(),2000);
}

/* FIREWORK (ADDED) */
function fire(){
    confetti({
        particleCount:120,
        spread:80,
        origin:{y:0.6}
    });
}

/* TEST */
function startTest(){
    closeAll();
    task.innerHTML="Technology is evolving rapidly in today's world";
}

/* FINISH TEST (ONLY ADD) */
function finishTest(){

    let wpm = 50; // placeholder (original logic untouched)

    if(wpm > bestWPM){
        bestWPM = wpm;
        fire();
        showPopup("🎉 New Best Score!");
    }
}

</script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
