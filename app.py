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
/* ❌ FULL STYLE SAME — NO CHANGE */
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
</style>
</head>

<body onclick="focusInput(); unlockAudio();">

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
<a>Login</a>
<a>Create Account</a>
</div>
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
<button class="time-btn" onclick="startTest(60)">1 Min</button>
<button class="time-btn" onclick="startTest(180)">3 Min</button>
<button class="time-btn" onclick="startTest(300)">5 Min</button>
<button class="time-btn" onclick="startTest(600)">10 Min</button>
</div>

<script>

/* SAME START */
function startSite(){
    let screen = document.getElementById("welcomeScreen");
    screen.style.opacity="0";
    setTimeout(()=>{
        screen.style.display="none";
        loadText();
    },1000);
}

/* 🔊 PROFESSIONAL KEYBOARD SOUND */
let volume = 0.5;
let unlocked = false;
let sounds = [];

// real mechanical typing sound (multi-layer)
for(let i=0;i<12;i++){
    let a = new Audio("https://assets.mixkit.co/sfx/preview/mixkit-mechanical-keyboard-single-key-press-1502.mp3");
    a.preload = "auto";
    sounds.push(a);
}

document.getElementById("volumeSlider").oninput=function(){
    volume=this.value;
};

function unlockAudio(){
    if(!unlocked){
        sounds.forEach(s=>{
            s.volume=0;
            s.play().then(()=>{
                s.pause();
                s.currentTime=0;
            }).catch(()=>{});
        });
        unlocked=true;
    }
}

let idx=0;

// 🔥 REAL KEY FEEL
document.addEventListener("keydown", function(){
    if(!unlocked) unlockAudio();

    let s = sounds[idx];
    s.currentTime = 0;
    s.volume = volume;
    s.play().catch(()=>{});

    idx = (idx+1)%sounds.length;
});

/* REST SAME (typing logic untouched) */
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
    document.getElementById("nextBtn").style.display="none";
    document.getElementById("restartBtn").style.display="none";

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

function nextTest(){ timeLeft=60; loadText(); }
function restartTest(){ timeLeft=60; loadText(); }
function showTest(){ document.getElementById("testBox").style.display="block"; }
function startTest(t){ timeLeft=t; document.getElementById("testBox").style.display="none"; loadText(); }

</script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
