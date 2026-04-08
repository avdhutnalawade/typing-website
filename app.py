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

/* HEADER */
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

/* CENTER */
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

/* TIMER */
#timer {
    font-size:28px;
    color:#00ffcc;
    text-shadow:0 0 10px #00ffff;
    margin-bottom:15px;
}

/* BUTTONS */
.btn {
    margin:15px;
    padding:12px 30px;
    border:none;
    border-radius:10px;
    background:linear-gradient(45deg,#00c6ff,#0072ff);
    color:white;
    font-size:16px;
    cursor:pointer;
    box-shadow:0 0 15px rgba(0,198,255,0.7);
    transition:0.3s;
}
.btn:hover {transform:scale(1.1);}

/* FIREWORK */
.firework {
    position:absolute;
    width:8px;
    height:8px;
    border-radius:50%;
    animation: explode 1s ease-out forwards;
}
@keyframes explode {
    0% {transform:scale(0); opacity:1;}
    100% {transform:scale(4); opacity:0;}
}

/* TEST BOX */
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
.time-btn:hover {transform:scale(1.1);}
</style>
</head>

<body onclick="focusInput()">

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

let paragraphs=[
"Technology is evolving rapidly in today's world and typing is an essential skill for everyone.",
"Practice daily to improve your typing speed and accuracy over time and build strong muscle memory.",
"Consistency and patience are key to mastering keyboard skills and becoming more efficient.",
"Focus on accuracy first and then speed will naturally improve with continuous practice."
];

let currentText="",timer,timeLeft=60;
let startTime,totalTyped=0,mistakes=0;
let lastWPM=0;

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
    totalTyped=0;
    mistakes=0;

    clearInterval(timer);
    timer=setInterval(updateTimer,1000);
}

function updateTimer(){
    timeLeft--;
    document.getElementById("timer").innerText="⏱ "+timeLeft+" sec";

    if(timeLeft<=0){
        finishTest();
    }
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

    mistakes=0;
    for(let i=0;i<input.length;i++){
        if(input[i]!==currentText[i]) mistakes++;
    }

    if(input===currentText){
        finishTest();
    }
});

function finishTest(){
    clearInterval(timer);

    let time=(new Date().getTime()-startTime)/60000;
    let wpm=Math.round(((totalTyped-mistakes)/5)/time);
    let acc=Math.round(((totalTyped-mistakes)/totalTyped)*100);

    let improvement="";
    if(lastWPM!==0){
        if(wpm>lastWPM) improvement="📈 Improved!";
        else if(wpm<lastWPM) improvement="📉 Try Again!";
        else improvement="😐 Same Speed!";
    }

    lastWPM=wpm;

    document.getElementById("result").innerHTML=
    "🎉 WPM: "+wpm+" | Accuracy: "+acc+"% <br>"+improvement;

    createFireworks();

    document.getElementById("nextBtn").style.display="inline-block";
    document.getElementById("restartBtn").style.display="inline-block";
}

function nextTest(){
    timeLeft=60;
    loadText();
}

function restartTest(){
    timeLeft=60;
    loadText();
}

function createFireworks(){
    for(let i=0;i<20;i++){
        let f=document.createElement("div");
        f.className="firework";
        f.style.background=`hsl(${Math.random()*360},100%,50%)`;
        f.style.left=Math.random()*window.innerWidth+"px";
        f.style.top=Math.random()*window.innerHeight+"px";
        document.body.appendChild(f);
        setTimeout(()=>f.remove(),1000);
    }
}

function showTest(){
    document.getElementById("testBox").style.display="block";
}

function startTest(t){
    timeLeft=t;
    document.getElementById("testBox").style.display="none";
    loadText();
}

loadText();

</script>

</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
