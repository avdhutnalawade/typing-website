from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return """
<!DOCTYPE html>  <html>  
<head>  
<title>Beginner Typing Speed Test</title>  
<link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@500&family=Pacifico&display=swap" rel="stylesheet">  
<style>  
body { margin:0; font-family:'Roboto Mono', monospace; background:#1a1a2e; color:white; overflow:hidden; }  
.left-menu{ position:fixed; top:120px; left:20px; display:flex; flex-direction:column; gap:10px; z-index:10000; }  
.left-menu button{ padding:10px; border:none; border-radius:6px; background:#00c6ff; color: white; cursor:pointer; font-weight: bold; }  
.modal{ position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); background:rgba(10, 10, 30, 0.98); padding:30px; border-radius:15px; display:none; z-index:99999; min-width: 400px; border: 2px solid #00c6ff; box-shadow: 0 0 30px rgba(0, 198, 255, 0.3); }  
.video-container { position: relative; padding-bottom: 56.25%; height: 0; }
.video-container iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
#statsTable { margin-top: 20px; max-height: 300px; overflow-y: auto; }
table { width: 100%; border-collapse: collapse; color: white; font-size: 14px; }
th, td { border: 1px solid #333; padding: 12px; text-align: center; }
th { background: #0072ff; color: white; }
.user-circle{ background:#00c6ff; padding:8px 15px; border-radius:20px; }  
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
.btn { margin:15px; padding:12px 30px; border:none; border-radius:10px; background:linear-gradient(45deg,#00c6ff,#0072ff); color:white; font-size:16px; cursor:pointer; }  
.test-box { position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); display:none; text-align:center; background:rgba(255,255,255,0.1); padding:25px; border-radius:15px; }  
</style>  
</head>  
<body onclick="focusInput();">  

<div class="left-menu">  
<button onclick="showTest()">Test</button>  
<button onclick="openLogin()">Login</button>  
<button onclick="openCreate()">Create Account</button>  
<button onclick="openTutorial()" style="background:#8a2be2;">Tutorials</button>
<button id="adminBtn" style="display:none; background:#ff4d4d;" onclick="openAdmin()">ADMIN PANEL</button>
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

<div class="modal" id="tutorialBox" onclick="event.stopPropagation()">
    <h3 style="color:#00ffff">Typing Tips & Tutorials</h3>
    <div class="video-container">
        <iframe src="https://www.youtube.com/embed/yv_Z_qZ8j_M" frameborder="0" allowfullscreen></iframe>
    </div>
    <button class="btn" style="background:gray; margin-top:15px;" onclick="closeAll()">Close</button>
</div>

<div class="modal" id="adminPanel" onclick="event.stopPropagation()">
    <h2 style="color:#00ffff">Admin Leaderboard</h2>
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
<div id="timer">⏱ 60 sec</div>  
<div id="task"></div>  
<input id="hiddenInput">  
<div id="result"></div>  <div>  
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
let users = {"admin":"1234"};  
let userStats = {"admin": { attempts: 0, bestWpm: 0, accuracy: 0 }};
let currentUser = null;  
  
function closeAll(){  
    loginBox.style.display="none";  
    createBox.style.display="none";  
    testBox.style.display="none";  
    adminPanel.style.display="none";
    tutorialBox.style.display="none";
    let iframe = tutorialBox.querySelector('iframe');
    let src = iframe.src;
    iframe.src = src;
}  
  
function openLogin(){ stopTyping(); closeAll(); loginBox.style.display="block"; username.focus(); }  
function openTutorial(){ stopTyping(); closeAll(); tutorialBox.style.display="block"; }

function login(){  
    let u = document.getElementById("username").value;  
    let p = document.getElementById("password").value;  
    if(users[u] && users[u] == p){  
        currentUser = u;  
        document.getElementById("userDisplay").innerHTML = "<span class='user-circle'>👤 "+u+"</span> <button onclick='logout()'>Logout</button>";  
        if(u === "admin") document.getElementById("adminBtn").style.display = "block";
        alert("Login Successful!"); closeAll();  
    } else { alert("Wrong Credentials"); }  
}  
  
function createAccount(){  
    let u = document.getElementById("newUsername").value;  
    let p = document.getElementById("newPassword").value;  
    if(u && p){  
        users[u] = p;  
        userStats[u] = { attempts: 0, bestWpm: 0, accuracy: 0 }; 
        alert("Account Created!"); closeAll();  
    }  
}  
  
function logout(){ currentUser = null; document.getElementById("userDisplay").innerHTML = ""; document.getElementById("adminBtn").style.display = "none"; }  

function openAdmin(){
    stopTyping(); closeAll();
    document.getElementById("adminPanel").style.display = "block";
    let sortedUsers = Object.keys(userStats).sort((a,b) => userStats[b].bestWpm - userStats[a].bestWpm);
    let html = "<table><tr><th>Rank</th><th>User</th><th>Tests</th><th>Max WPM</th><th>Accuracy</th></tr>";
    sortedUsers.forEach((name, index) => {
        let s = userStats[name];
        html += `<tr><td>#${index + 1}</td><td>${name}</td><td>${s.attempts}</td><td>${s.bestWpm}</td><td>${s.accuracy}%</td></tr>`;
    });
    html += "</table>";
    document.getElementById("statsTable").innerHTML = html;
}
  
function stopTyping(){ clearInterval(timer); hiddenInput.blur(); }  
  
const typeSound = new Audio('https://www.soundjay.com/communication/typewriter-key-1.mp3');
function playKeySound(){  
    typeSound.currentTime = 0;
    typeSound.play().catch(e => console.log("Sound blocked"));
}  
  
let paragraphs=["Technology is evolving rapidly in today's world and typing is an essential skill for everyone."];  
let currentText="",timer,timeLeft=60;  
let startTime,totalTyped=0;  
  
function loadText(){  
    result.innerHTML=""; nextBtn.style.display="none"; restartBtn.style.display="none";  
    currentText=paragraphs[0];  
    let html="";  
    for(let i=0;i<currentText.length;i++){ html+="<span>"+currentText[i]+"</span>"; }  
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
  
function focusInput(){ hiddenInput.focus(); }  
  
hiddenInput.addEventListener("input", function(){  
    playKeySound();  
    let input = this.value;  
    let spans = document.querySelectorAll("#task span");  
    totalTyped = input.length;  
  
    for(let i=0; i<spans.length; i++){  
        if(input[i] == null) spans[i].classList.remove("correct","wrong");  
        else if(input[i] === currentText[i]){ spans[i].classList.add("correct"); spans[i].classList.remove("wrong"); } 
        else { spans[i].classList.add("wrong"); spans[i].classList.remove("correct"); }  
    }  
    
    if(input === currentText) {
        clearInterval(timer); 
        finishTest(); 
    }
});  
  
function finishTest(){  
    clearInterval(timer);  
    let timeSpent = (new Date().getTime()-startTime)/60000;  
    let wpm = Math.round((totalTyped/5)/timeSpent) || 0;  
    let correctChars = document.querySelectorAll(".correct").length;
    let acc = totalTyped > 0 ? Math.round((correctChars / totalTyped) * 100) : 0;
  
    result.innerHTML="🎉 WPM: "+wpm + " | Accuracy: " + acc + "%";  
  
    if(currentUser) {
        userStats[currentUser].attempts++;
        if(wpm > userStats[currentUser].bestWpm) userStats[currentUser].bestWpm = wpm;
        userStats[currentUser].accuracy = acc;
    }
    nextBtn.style.display="inline-block"; restartBtn.style.display="inline-block";  
}  
  
function nextTest(){ timeLeft=60; loadText(); }  
function restartTest(){ timeLeft=60; loadText(); }  
function showTest(){ stopTyping(); closeAll(); testBox.style.display="block"; }  
function startTest(t){ timeLeft=t; testBox.style.display="none"; loadText(); }  
function startSite(){ welcomeScreen.style.display="none"; loadText(); }  
</script>  
</body>  
</html>  
"""

if __name__ == "__main__":
    app.run(debug=True)
