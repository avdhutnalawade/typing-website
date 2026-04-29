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
/* 🔥 SAME STYLE */
body {
    margin:0;
    font-family:'Roboto Mono', monospace;
    background:#1a1a2e;
    color:white;
    overflow:hidden;
}

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

.nav-buttons a {
    background:#00c6ff;
    padding:10px 20px;
    margin-left:10px;
    border-radius:6px;
    cursor:pointer;
}

.center {
    position:absolute;
    top:55%;
    left:50%;
    transform:translate(-50%,-50%);
    width:80%;
    text-align:center;
}

#task { font-size:32px; line-height:2; color:#aaa; }
.correct {color:#00ff88;}
.wrong {color:#ff4d4d;}

#hiddenInput { opacity:0; position:absolute; }

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

.test-box {
    position:absolute;
    top:60%;
    left:50%;
    transform:translate(-50%,-50%);
    display:none;
    text-align:center;
    background:rgba(255,255,255,0.1);
    padding:25px;
    border-radius:15px;
}

.time-btn {
    margin:8px;
    padding:12px 22px;
    border:none;
    border-radius:8px;
    background:linear-gradient(45deg,#00c6ff,#0072ff);
    color:white;
    cursor:pointer;
}

.volume-box{
    position:fixed;
    bottom:20px;
    right:20px;
}

/* 🔥 LOGIN POPUP */
.login-box{
    position:fixed;
    top:50%;
    left:50%;
    transform:translate(-50%,-50%);
    background:#222;
    padding:20px;
    border-radius:10px;
    display:none;
    z-index:9999;
}
.login-box input{
    display:block;
    margin:10px 0;
    padding:8px;
}
</style>
</head>

<body onclick="focusInput(); unlockAudio();">

<!-- LOGIN BOX -->
<div class="login-box" id="loginBox">
<h3>Login</h3>
<input type="text" id="username" placeholder="Username">
<input type="password" id="password" placeholder="Password">
<button onclick="login()">Login</button>
</div>

<!-- 🔥 WELCOME SCREEN -->
<div id="welcomeScreen">
    <div id="welcomeText">Welcome 🚀</div>
    <button class="start-btn" onclick="startSite()">Start</button>
</div>

<div class="volume-box">
🔊 <input type="range" min="0" max="1" step="0.05" value="0.5" id="volumeSlider">
</div>

<div class="header">
<h2>Welcome to Beginner Typing Speed Test</h2>
<div class="nav-buttons">
<a onclick="showTest()">Test</a>
<a onclick="openLogin()">Login</a>
<span id="userDisplay"></span>
</div>
</div>

<div class="center">
<div id="timer"></div>
<div id="task"></div>
<input id="hiddenInput">
<div id="result"></div>
</div>

<script>

/* 🔥 LOGIN SYSTEM */
let users = {"admin":"1234"};

function openLogin(){
    document.getElementById("loginBox").style.display="block";
}

function login(){
    let u=document.getElementById("username").value;
    let p=document.getElementById("password").value;

    if(users[u] && users[u]==p){
        document.getElementById("userDisplay").innerText="👤 "+u;
        alert("Login Successful ✅");
        document.getElementById("loginBox").style.display="none";
    } else{
        alert("Wrong Username or Password ❌");
    }
}

/* 🔥 ORIGINAL CODE BELOW SAME */
function startSite(){
    let screen = document.getElementById("welcomeScreen");
    screen.style.opacity="0";
    setTimeout(()=>{
        screen.style.display="none";
        loadText();
    },1000);
}

let volume = 0.5;
let unlocked = false;
let audioCtx;

document.getElementById("volumeSlider").oninput=function(){
    volume=this.value;
};

function unlockAudio(){
    if(!unlocked){
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        unlocked = true;
    }
}

function playKeySound(){
    if(!unlocked) return;

    let osc = audioCtx.createOscillator();
    let gain = audioCtx.createGain();

    osc.type = "square";
    osc.frequency.value = 200 + Math.random()*100;

    gain.gain.value = volume * 0.2;

    osc.connect(gain);
    gain.connect(audioCtx.destination);

    osc.start();
    osc.stop(audioCtx.currentTime + 0.05);
}

let paragraphs=[
"Technology is evolving rapidly in today's world and typing is an essential skill for everyone.",
"Practice daily to improve your typing speed and accuracy over time and build strong muscle memory.",
"Consistency and patience are key to mastering keyboard skills and becoming more efficient.",
"Focus on accuracy first and then speed will naturally improve with continuous practice."
];

let currentText="",timer,timeLeft=60;
let startTime,totalTyped=0;

function loadText(){
    document.getElementById("result").innerHTML="";
    currentText=paragraphs[Math.floor(Math.random()*paragraphs.length)];

    let html="";
    for(let i=0;i<currentText.length;i++){
        html+="<span>"+currentText[i]+"</span>";
    }
    document.getElementById("task").innerHTML=html;

    document.getElementById("hiddenInput").value="";
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
    document.getElementById("hiddenInput").focus();
}

document.getElementById("hiddenInput").addEventListener("input",function(){

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
    document.getElementById("result").innerHTML="🎉 WPM: "+wpm;
}

function showTest(){
    document.getElementById("testBox").style.display="block";
}

function startTest(t){
    timeLeft=t;
    document.getElementById("testBox").style.display="none";
    loadText();
}

</script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
