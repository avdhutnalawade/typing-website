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

<!-- 🎆 ADDED LIBRARY -->
<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>

<style>

/* ===================== ORIGINAL BODY ===================== */
body {
    margin:0;
    font-family:'Roboto Mono', monospace;
    background:#1a1a2e;
    color:white;
    overflow:hidden;
}

/* ===================== LEFT MENU ===================== */
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

/* ===================== MODAL ===================== */
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

/* ===================== USER UI ===================== */
.user-circle{
    background:#00c6ff;
    padding:8px 15px;
    border-radius:20px;
}

/* ===================== POPUP (ADDED) ===================== */
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
    z-index:99999;
}

@keyframes fade{
    0%{opacity:0; transform:translate(-50%,-20px);}
    50%{opacity:1;}
    100%{opacity:0; transform:translate(-50%,0);}
}

/* ===================== ORIGINAL SCREEN ===================== */
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

/* ===================== HEADER ===================== */
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

/* ===================== CENTER ===================== */
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
}

/* ===================== TEST BOX ===================== */
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

/* ===================== BUTTON ===================== */
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

</style>
</head>

<body onclick="focusInput(); unlockAudio();">

<!-- LEFT MENU -->
<div class="left-menu">
<button onclick="showTest()">Test</button>
<button onclick="openLogin()">Login</button>
<button onclick="openCreate()">Create Account</button>
</div>

<!-- LOGIN -->
<div class="modal" id="loginBox">
<h3>Login</h3>
<input type="text" id="username">
<input type="password" id="password">
<button onclick="login()">Login</button>
</div>

<!-- CREATE -->
<div class="modal" id="createBox">
<h3>Create Account</h3>
<input type="text" id="newUsername">
<input type="password" id="newPassword">
<button onclick="createAccount()">Create</button>
</div>

<!-- WELCOME -->
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
</div>

<div class="test-box" id="testBox">
<button onclick="startTest(60)">1 Min</button>
</div>

<script>

/* ================= USERS ================= */
let users={"admin":"1234"};
let currentUser=null;

let correctTyped=0;
let bestWPM=0;

/* ================= AUDIO ================= */
let audioCtx;
function unlockAudio(){
 if(!audioCtx){
  audioCtx=new (window.AudioContext||window.webkitAudioContext)();
 }
}

/* ================= POPUP ================= */
function showPopup(msg){
 let div=document.createElement("div");
 div.className="popup-msg";
 div.innerText=msg;
 document.body.appendChild(div);
 setTimeout(()=>div.remove(),2000);
}

/* ================= FIREWORK ================= */
function fire(){
 confetti({
  particleCount:120,
  spread:80,
  origin:{y:0.6}
 });
}

/* ================= TEXT ================= */
let paragraphs=[
"Technology is evolving rapidly in today's world and typing is an essential skill for everyone."
];

let currentText="",timer,timeLeft=60;
let startTime,totalTyped=0;

/* ================= LOAD ================= */
function loadText(){
 result.innerHTML="";
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

/* ================= TIMER ================= */
function updateTimer(){
 timeLeft--;
 timer.innerText="⏱ "+timeLeft;
 if(timeLeft<=0) finishTest();
}

/* ================= INPUT ================= */
function focusInput(){
 hiddenInput.focus();
}

hiddenInput.addEventListener("input",function(){

 let input=this.value;
 let spans=document.querySelectorAll("#task span");

 totalTyped=input.length;
 correctTyped=0;

 for(let i=0;i<spans.length;i++){
  if(input[i]===currentText[i]){
   spans[i].classList.add("correct");
   correctTyped++;
  } else {
   spans[i].classList.add("wrong");
  }
 }

 if(input===currentText) finishTest();
});

/* ================= FINISH ================= */
function finishTest(){
 clearInterval(timer);

 let wpm=Math.round((totalTyped/5)/((new Date().getTime()-startTime)/60000));
 let accuracy=Math.round((correctTyped/totalTyped)*100)||0;

 result.innerHTML="🎉 WPM: "+wpm+"<br>🎯 Accuracy: "+accuracy+"%";

 if(wpm>bestWPM){
  bestWPM=wpm;
  fire();
  showPopup("🎉 New Best Score!");
 }
}

/* ================= START ================= */
function startSite(){
 welcomeScreen.style.display="none";
 loadText();
}

function showTest(){
 testBox.style.display="block";
}

function startTest(t){
 timeLeft=t;
 testBox.style.display="none";
 loadText();
}

</script>

</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
