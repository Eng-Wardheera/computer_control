import time

import time
from flask import Flask, render_template_string, request, jsonify
import os
import screen_brightness_control as sbc
import psutil
import keyboard
import pygetwindow as gw

# =============================
# SOUND CONTROL
# =============================

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

app = Flask(__name__)

# =============================
# VOLUME SETUP
# =============================

try:

    devices = AudioUtilities.GetSpeakers()

    interface = devices.Activate(
        IAudioEndpointVolume._iid_,
        CLSCTX_ALL,
        None
    )

    volume = cast(
        interface,
        POINTER(IAudioEndpointVolume)
    )

except:

    volume = None


# =============================
# HTML TEMPLATE
# =============================

HTML = """

<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Advanced Dashboard</title>

<style>

*{
    margin:0;
    padding:0;
    box-sizing:border-box;
    font-family:Arial;
}

body{
    background:#050816;
    color:white;
}

/* SIDEBAR */

.sidebar{
    position:fixed;
    left:0;
    top:0;
    width:260px;
    height:100vh;
    background:#0c1224;
    padding:25px;
}

.logo{
    font-size:28px;
    color:cyan;
    font-weight:bold;
    margin-bottom:40px;
}

.menu button{
    width:100%;
    padding:15px;
    margin-top:10px;
    border:none;
    border-radius:15px;
    background:#111827;
    color:white;
    cursor:pointer;
    font-size:16px;
}

.menu button:hover{
    background:cyan;
    color:black;
}

.dropdown{
    display:none;
    padding-left:10px;
}

.dropdown a{
    display:block;
    padding:12px;
    margin-top:8px;
    background:#131c31;
    color:white;
    text-decoration:none;
    border-radius:10px;
}

/* MAIN */

.main{
    margin-left:260px;
    padding:30px;
}

.topbar{
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:30px;
}

.topbar h1{
    color:cyan;
}

.grid{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(320px,1fr));
    gap:25px;
}

.card{
    background:rgba(255,255,255,0.05);
    border-radius:25px;
    padding:25px;
    border:1px solid rgba(255,255,255,0.08);
}

.card h2{
    color:cyan;
    margin-bottom:20px;
}

.status{
    font-size:35px;
    margin-bottom:20px;
}

input[type=range]{
    width:100%;
    margin-bottom:20px;
}

.action{
    width:100%;
    padding:15px;
    border:none;
    border-radius:15px;
    background:cyan;
    color:black;
    font-weight:bold;
    cursor:pointer;
}

.shutdown{
    background:red;
    color:white;
    margin-top:10px;
}

.restart{
    background:orange;
    color:black;
    margin-top:10px;
}

</style>

</head>
<body>

<!-- SIDEBAR -->

<div class="sidebar">

    <div class="logo">
        ⚡ SYSTEM UI
    </div>

    <div class="menu">

        <button onclick="toggleMenu('systemMenu')">
            System Controls ▼
        </button>

        <div class="dropdown" id="systemMenu">

            <a href="#">Brightness</a>
            <a href="#">Volume</a>
            <a href="#">Keyboard RGB</a>

        </div>

        <button onclick="toggleMenu('powerMenu')">
            Power Options ▼
        </button>

        <div class="dropdown" id="powerMenu">

            <a href="#">Shutdown</a>
            <a href="#">Restart</a>

        </div>

    </div>

</div>


<!-- MAIN -->

<div class="main">

    <div class="topbar">

        <h1>ADVANCED SYSTEM DASHBOARD</h1>

    </div>

    <div class="grid">

    

        <!-- BRIGHTNESS -->

        <div class="card">

            <h2>Brightness</h2>

            <div class="status" id="brightnessValue">
                50%
            </div>

            <input
                type="range"
                min="0"
                max="100"
                value="50"
                id="brightnessSlider"
            >

            <button
                class="action"
                onclick="setBrightness()"
            >
                APPLY
            </button>

        </div>


        <!-- VOLUME -->

        <div class="card">

            <h2>Volume</h2>

            <div class="status" id="volumeValue">
                50%
            </div>

            <input
                type="range"
                min="0"
                max="100"
                value="50"
                id="volumeSlider"
            >

            <button
                class="action"
                onclick="setVolume()"
            >
                APPLY
            </button>

        </div>


        <!-- KEYBOARD -->

        <div class="card">

            <h2>Keyboard RGB</h2>

            <div class="status">
                READY
            </div>

            <button
                class="action"
                onclick="keyboardLight()"
            >
                TOGGLE RGB
            </button>

        </div>

        <!-- SYSTEM MONITOR -->

<div class="card">

    <h2>System Monitor</h2>

    <div style="margin-top:20px;">

        <div style="margin-bottom:20px;">

            <h3>CPU Usage</h3>

            <div class="status" id="cpuUsage">
                0%
            </div>

        </div>

        <div style="margin-bottom:20px;">

            <h3>RAM Usage</h3>

            <div class="status" id="ramUsage">
                0%
            </div>

        </div>

        <div style="margin-bottom:20px;">

            <h3>Battery</h3>

            <div class="status" id="batteryLevel">
                0%
            </div>

        </div>

        <div>

            <h3>Current Time</h3>

            <div class="status" id="currentTime">
                --:--
            </div>

        </div>

        <button
            class="action"
            onclick="loadSystemInfo()"
        >
            REFRESH
        </button>

    </div>

</div>

        <!-- RUNNING PROGRAMS -->

<div class="card">

    <h2>Running Programs</h2>

    <div id="processList">

        Loading programs...

    </div>

</div>

<!-- CHROME TABS -->

<div class="card">

    <h2>Chrome Tabs</h2>

    <div id="chromeTabs">

        Loading tabs...

    </div>

</div>



        <!-- POWER -->

        <div class="card">

            <h2>Power</h2>

            <button
                class="action shutdown"
                onclick="shutdownPC()"
            >
                SHUTDOWN
            </button>

            <button
                class="action restart"
                onclick="restartPC()"
            >
                RESTART
            </button>

        </div>

    </div>

</div>



<script>

function toggleMenu(id){

    const menu = document.getElementById(id)

    if(menu.style.display === "block"){

        menu.style.display = "none"

    }else{

        menu.style.display = "block"

    }

}


/* BRIGHTNESS */

const brightnessSlider =
    document.getElementById('brightnessSlider')

const brightnessValue =
    document.getElementById('brightnessValue')

brightnessSlider.oninput = () => {

    brightnessValue.innerText =
        brightnessSlider.value + "%"

}


async function setBrightness(){

    await fetch('/brightness',{

        method:'POST',

        headers:{
            'Content-Type':'application/json'
        },

        body:JSON.stringify({
            value:brightnessSlider.value
        })

    })

    alert("Brightness Updated")

}



/* VOLUME */

const volumeSlider =
    document.getElementById('volumeSlider')

const volumeValue =
    document.getElementById('volumeValue')

volumeSlider.oninput = () => {

    volumeValue.innerText =
        volumeSlider.value + "%"

}


async function setVolume(){

    await fetch('/volume',{

        method:'POST',

        headers:{
            'Content-Type':'application/json'
        },

        body:JSON.stringify({
            value:volumeSlider.value
        })

    })

    alert("Volume Updated")

}



/* KEYBOARD */

async function keyboardLight(){

    await fetch('/keyboard-light',{

        method:'POST'

    })

    alert("Keyboard RGB Toggled")

}






/* SHUTDOWN */

async function shutdownPC(){

    if(confirm("Shutdown PC?")){

        await fetch('/shutdown',{

            method:'POST'

        })

    }

}



/* RESTART */

async function restartPC(){

    if(confirm("Restart PC?")){

        await fetch('/restart',{

            method:'POST'

        })

    }

}



/* =========================
   LOAD CHROME + EDGE TABS
========================= */

async function loadChromeTabs(){

    const response =
        await fetch('/chrome-tabs')

    const data =
        await response.json()

    const chromeTabs =
        document.getElementById('chromeTabs')

    chromeTabs.innerHTML = ""

    data.tabs.forEach(tab => {

        chromeTabs.innerHTML += `

        <div style="
            background:#111827;
            padding:12px;
            border-radius:12px;
            margin-top:10px;
        ">

            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                gap:10px;
            ">

                <div style="
                    color:white;
                    font-size:14px;
                    word-break:break-word;
                    flex:1;
                ">

                    ${tab.title}

                </div>

                <button
                    onclick="closeBrowserTab(
                        \`${tab.title}\`
                    )"
                    style="
                        background:red;
                        color:white;
                        border:none;
                        padding:10px;
                        border-radius:10px;
                        cursor:pointer;
                    "
                >
                    CLOSE
                </button>

            </div>

        </div>

        `

    })

}


/* =========================
   CLOSE TAB
========================= */

async function closeBrowserTab(title){

    const confirmClose =
        confirm(
            "Close this browser tab/window?"
        )

    if(confirmClose){

        await fetch('/close-browser-tab',{

            method:'POST',

            headers:{
                'Content-Type':'application/json'
            },

            body:JSON.stringify({
                title:title
            })

        })

        loadChromeTabs()

    }

}


/* AUTO REFRESH */

setInterval(loadChromeTabs, 4000)

loadChromeTabs()



    /* =========================
   LOAD PROGRAMS
========================= */

async function loadProcesses(){

    const response = await fetch('/processes')

    const data = await response.json()

    const processList =
        document.getElementById('processList')

    processList.innerHTML = ""

    data.processes.forEach(process => {

        processList.innerHTML += `

        <div style="
            background:#111827;
            padding:12px;
            border-radius:12px;
            margin-top:10px;
        ">

            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
            ">

                <div>

                    <b>${process.name}</b>

                    <br>

                    PID: ${process.pid}

                </div>

                <button
                    onclick="closeProcess(${process.pid})"
                    style="
                        background:red;
                        color:white;
                        border:none;
                        padding:10px;
                        border-radius:10px;
                        cursor:pointer;
                    "
                >
                    CLOSE
                </button>

            </div>

        </div>

        `

    })

}


/* =========================
   CLOSE PROCESS
========================= */

async function closeProcess(pid){

    const confirmClose =
        confirm("Close this program?")

    if(confirmClose){

        await fetch('/close-process',{

            method:'POST',

            headers:{
                'Content-Type':'application/json'
            },

            body:JSON.stringify({
                pid:pid
            })

        })

        loadProcesses()

    }

}


/* AUTO LOAD */

loadProcesses()



/* =========================
   SYSTEM INFO
========================= */

async function loadSystemInfo(){

    const response =
        await fetch('/system-info')

    const data =
        await response.json()

    document.getElementById('cpuUsage')
        .innerText = data.cpu + "%"

    document.getElementById('ramUsage')
        .innerText = data.ram + "%"

    document.getElementById('batteryLevel')
        .innerText = data.battery + "%"

}


/* =========================
   CLOCK
========================= */

function updateClock(){

    const now = new Date()

    const time =
        now.toLocaleTimeString()

    document.getElementById(
        'currentTime'
    ).innerText = time

}


/* AUTO UPDATE */

setInterval(loadSystemInfo, 3000)

setInterval(updateClock, 1000)

loadSystemInfo()

updateClock()




</script>

</body>
</html>

"""


# =============================
# HOME
# =============================

@app.route('/')
def home():

    return render_template_string(HTML)


# =============================
# BRIGHTNESS
# =============================

@app.route('/brightness', methods=['POST'])
def brightness():

    try:

        value = int(request.json['value'])

        sbc.set_brightness(value)

        return jsonify({
            'status':'success',
            'brightness':value
        })

    except Exception as e:

        return jsonify({
            'status':'error',
            'message':str(e)
        })


# =============================
# VOLUME
# =============================

@app.route('/volume', methods=['POST'])
def set_volume():

    try:

        if volume:

            value = int(request.json['value'])

            volume.SetMasterVolumeLevelScalar(
                value / 100,
                None
            )

            return jsonify({
                'status':'success',
                'volume':value
            })

        else:

            return jsonify({
                'status':'error',
                'message':'Volume system failed'
            })

    except Exception as e:

        return jsonify({
            'status':'error',
            'message':str(e)
        })


# =============================
# SHUTDOWN
# =============================

@app.route('/shutdown', methods=['POST'])
def shutdown():

    os.system('shutdown /s /t 1')

    return jsonify({
        'status':'shutdown'
    })


# =============================
# RESTART
# =============================

@app.route('/restart', methods=['POST'])
def restart():

    os.system('shutdown /r /t 1')

    return jsonify({
        'status':'restart'
    })


# =============================
# CHROME TABS
# =============================
@app.route('/chrome-tabs')
def chrome_tabs():

    tabs = []

    try:

        windows = gw.getAllWindows()

        for window in windows:

            try:

                title = window.title

                if title and len(title) > 2:

                    browser_keywords = [

                        'Chrome',
                        'Google Chrome',
                        'Edge',
                        'Microsoft Edge'

                    ]

                    if any(

                        keyword in title

                        for keyword in browser_keywords

                    ):

                        tabs.append({

                            'title': title,
                            'left': window.left,
                            'top': window.top,
                            'width': window.width,
                            'height': window.height

                        })

            except:
                pass

        # REMOVE DUPLICATES

        unique_tabs = []

        seen = set()

        for tab in tabs:

            if tab['title'] not in seen:

                seen.add(tab['title'])

                unique_tabs.append(tab)

        return jsonify({

            'tabs': unique_tabs

        })

    except Exception as e:

        return jsonify({

            'status': 'error',
            'message': str(e)

        })
    

# =============================
# CLOSE BROWSER TAB/WINDOW
# =============================

@app.route('/close-browser-tab', methods=['POST'])
def close_browser_tab():
    import pyautogui

    try:

        title = request.json['title']

        windows = gw.getWindowsWithTitle(title)

        if not windows:

            return jsonify({

                'status':'error',
                'message':'Tab not found'

            })

        window = windows[0]

        # RESTORE IF MINIMIZED

        try:
            window.restore()
        except:
            pass

        time.sleep(0.5)

        # ACTIVATE WINDOW

        try:
            window.activate()
        except:
            pass

        time.sleep(1)

        # CLICK CENTER OF WINDOW

        center_x = (
            window.left +
            (window.width // 2)
        )

        center_y = (
            window.top +
            50
        )

        pyautogui.click(
            center_x,
            center_y
        )

        time.sleep(0.5)

        # CTRL + W

        pyautogui.hotkey(
            'ctrl',
            'w'
        )

        return jsonify({

            'status':'success',
            'message':'Tab closed'

        })

    except Exception as e:

        return jsonify({

            'status':'error',
            'message':str(e)

        })

# =============================
# KEYBOARD LIGHT
# =============================
keyboard_light_state = False
@app.route('/keyboard-light', methods=['POST'])
def keyboard_light():

    global keyboard_light_state

    try:

        if keyboard_light_state:

            # OFF
            keyboard.press_and_release(
                'fn+space'
            )

            keyboard_light_state = False

            return jsonify({

                'status':'success',
                'message':'Keyboard light OFF'

            })

        else:

            # ON
            keyboard.press_and_release(
                'fn+space'
            )

            keyboard_light_state = True

            return jsonify({

                'status':'success',
                'message':'Keyboard light ON'

            })

    except Exception as e:

        return jsonify({

            'status':'error',
            'message':str(e)

        })


# =============================
# SYSTEM INFO
# =============================
@app.route('/system-info')
def system_info():

    try:

        cpu = psutil.cpu_percent()

        ram = psutil.virtual_memory().percent

        battery_data = psutil.sensors_battery()

        battery = 0

        if battery_data:

            battery = battery_data.percent

        return jsonify({

            'cpu': cpu,
            'ram': ram,
            'battery': battery

        })

    except Exception as e:

        return jsonify({

            'status':'error',
            'message':str(e)

        })
    

# =============================
# GET RUNNING PROGRAMS
# =============================
@app.route('/processes')
def get_processes():

    processes = []

    for proc in psutil.process_iter([

        'pid',
        'name'

    ]):

        try:

            processes.append({

                'pid': proc.info['pid'],
                'name': proc.info['name']

            })

        except:

            pass

    return jsonify({
        'processes': processes[:50]
    })


# =============================
# CLOSE PROCESS
# =============================
@app.route('/close-process', methods=['POST'])
def close_process():

    try:

        pid = request.json['pid']

        process = psutil.Process(pid)

        process.terminate()

        return jsonify({

            'status':'success',
            'message':'Program closed'

        })

    except Exception as e:

        return jsonify({

            'status':'error',
            'message':str(e)

        })


# =============================
# RUN
# =============================
if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )