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

/* USERS (ADDED) */
let users = {"admin":"1234"};
let currentUser = null;

/* CLOSE ALL (ADDED) */
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
    username.focus();
}

function login(){
    let u=username.value;
    let p=password.value;

    if(users[u] && users[u]==p){
        currentUser=u;
        userDisplay.innerHTML = "<span class='user-circle'>👤 "+u+"</span> <button onclick='logout()'>Logout</button>";
        alert("Login Successful");
        closeAll();
    } else{
        alert("Wrong Username or Password");
    }
}

/* CREATE */
function openCreate(){
    stopTyping();
    closeAll();
    createBox.style.display="block";
    newUsername.focus();
}

function createAccount(){
    let u=newUsername.value;
    let p=newPassword.value;

    if(u && p){
        users[u]=p;
        alert("Account Created");
        closeAll();
    } else{
        alert("Enter Username & Password");
    }
}

/* LOGOUT */
function logout(){
    currentUser=null;
    userDisplay.innerHTML="";
}

/* STOP TYPING (ADDED) */
function stopTyping(){
    clearInterval(timer);
    hiddenInput.blur();
}

/* ORIGINAL AUDIO */
let audioCtx;
let volume = 0.1;

function unlockAudio(){
    if(!audioCtx){
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
}

function playKeySound(){
    if(!audioCtx) return;

    let osc = audioCtx.createOscillator();
    let gain = audioCtx.createGain();

    osc.type = "square";
    osc.frequency.value = 200 + Math.random()*100;
    gain.gain.value = volume;

    osc.connect(gain);
    gain.connect(audioCtx.destination);

    osc.start();
    osc.stop(audioCtx.currentTime + 0.05);
}

/* ORIGINAL TEST LOGIC */
let paragraphs=[
"Technology is evolving rapidly in today's world and typing is an essential skill for everyone."
];

let currentText="",timer,timeLeft=60;
let startTime,totalTyped=0;

function loadText(){
    result.innerHTML="";
    nextBtn.style.display="none";
    restartBtn.style.display="none";

    currentText=paragraphs[0];

    let html="";
    for(let i=0;i<currentText.length;i++){
        html+="<span>"+currentText[i]+"</span>";
    }
    task.innerHTML=html;

    hiddenInput.value="";
    startTime=new Date().getTime();

    clearInterval(timer);
    timer=setInterval(updateTimer,1000);
}

function updateTimer(){
    timeLeft--;
    document.getElementById("timer").innerText="⏱ "+timeLeft+" sec";
    if(timeLeft<=0) finishTest();
}

function focusInput(){
    hiddenInput.focus();
}

hiddenInput.addEventListener("input",function(){

    playKeySound();

    let input=this.value;
    let spans=document.querySelectorAll("#task span");

    totalTyped=input.length;

    for(let i=0;i<spans.length;i++){
        if(input[i]==null){
            spans[i].classList.remove("correct","wrong");
        }
        else if(input[i]===currentText[i]){
            spans[i].classList.add("correct");
            spans[i].classList.remove("wrong");
        } else {
            spans[i].classList.add("wrong");
            spans[i].classList.remove("correct");
        }
    }

    if(input===currentText) finishTest();
});

function finishTest(){
    clearInterval(timer);

    let time=(new Date().getTime()-startTime)/60000;
    let wpm=Math.round((totalTyped/5)/time);

    result.innerHTML="🎉 WPM: "+wpm;

    nextBtn.style.display="inline-block";
    restartBtn.style.display="inline-block";
}

function nextTest(){ timeLeft=60; loadText(); }
function restartTest(){ timeLeft=60; loadText(); }

function showTest(){
    stopTyping();
    closeAll();
    testBox.style.display="block";
}

function startTest(t){
    timeLeft=t;
    testBox.style.display="none";
    loadText();
}

function startSite(){
    welcomeScreen.style.display="none";
    loadText();
}

</script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
