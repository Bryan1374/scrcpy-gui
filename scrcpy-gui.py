import PySimpleGUI as gui
import json
from os import path
from os import system
import platform
from datetime import datetime


gui.theme("DarkGray5")

database_file = "db.json"

def make_window(layout):
    return gui.Window(title="scrcpy-gui", layout=layout, resizable=False)

def make_empty_db_data():
    return {
        "startWithScreenOff": True,
        "keepAwake": True,
        "alwaysOnTop": False,
        "disconnectDebugger" : True,
        "connections": []
    }

def get_data():
    if(not path.exists(database_file)):
        data = make_empty_db_data()
        with open(database_file, "w") as f:
            json.dump(data, f)
    else:
        with open(database_file, "r") as d:
            s = d.read()
            data = json.loads(s)
    return data

def save_data(data):
    with open(database_file, "w") as f:
        json.dump(data, f)

def make_layout(data):
    l = [
        [
            gui.Button(button_text="+", size=(2, 1)), 
            gui.Button(button_text="?", size=(2, 1), key="Help"),
            gui.Button(button_text="⚙️", size=(2, 1), key="Settings")
        ]
    ]
    for connection in data["connections"]:
        l.append([
            gui.Text(connection["name"], size=(20, 1)),
            gui.Button("x", size=(1, 1), key=("Delete", connection["name"])),
            gui.Button("🔴", size=(2, 1), key=("Record", connection["name"], connection["hostname"], connection["port"])),
            gui.Button("Pair", size=(4, 1), key=("Pair", connection["name"], connection["hostname"])),
            gui.Button(">", size=(2, 1), key=("Connect", connection["name"], connection["hostname"], connection["port"]))
            ])
    return l

def make_connection():
    dialog_layout = [
        [gui.Text("Connection name:", size=(20, 1)), gui.InputText(size=(50, 1))],
        [gui.Text("Hostname:", size=(20, 1)), gui.InputText(size=(50, 1))],
        [gui.Text("Port:", size=(20, 1)), gui.InputText(size=(50, 1))],
        [gui.Submit("Ok"), gui.Cancel("Cancel")]
        ]
    dialog_window = gui.Window(title="New connection", layout=dialog_layout, resizable=False, no_titlebar=True, keep_on_top=True, finalize=True)
    res, value = dialog_window.read()
    if res == "Ok":
        dialog_window.close()
        return { "name": value[0], "hostname": value[1], "port": value[2] }
    elif res == "Cancel":
        dialog_window.close()
        return None

def check_command_existance(command):
    if platform.system() == "Windows":
        return system(f"where {command}") == 0
    else:
        return system(f"which {command}") == 0

def get_commands_existance():
    return [ ("adb", check_command_existance("adb")), ("scrcpy", check_command_existance("scrcpy"))]

def make_settings_gui(data):
    settings_layout = [
        [gui.Checkbox("Start with phone screen off", size=(50, 1), default="startWithScreenOff" in data and data["startWithScreenOff"])],
        [gui.Checkbox("Keep awake", size=(50, 1), default="keepAwake" in data and data["keepAwake"])],
        [gui.Checkbox("Always on top", size=(50, 1), default="alwaysOnTop" in data and data["alwaysOnTop"])],
        [gui.Checkbox("Disconnect debugger when finished", size=(50, 1), default="disconnectDebugger" in data and data["disconnectDebugger"])],
        [gui.Submit("Ok"), gui.Cancel("Cancel")]
    ]
    settings_window = gui.Window("Settings", layout=settings_layout, resizable=False, no_titlebar=True, keep_on_top=True, finalize=True)
    cont = True
    while cont:
        ev, val = settings_window.read()
        if ev == "Cancel":
            cont = False
        elif ev == "Ok":
            data["startWithScreenOff"] = val[0]
            data["keepAwake"] = val[1]
            data["alwaysOnTop"] = val[2]
            data["disconnectDebugger"] = val[3]
            save_data(data)
            cont = False
    settings_window.close()
    return data

def get_record_file_name(name):
    now = datetime.now().strftime("%d%m%Y%H%M%S")
    return f"{name}-{now}.mp4"

def make_scrcpy_command(name, hostname, port, data, record):
    return f"scrcpy {'--turn-screen-off' if 'startWithScreenOff' in data and data['startWithScreenOff'] else ''} {'--stay-awake' if 'keepAwake' in data and data['keepAwake'] else ''} {'--always-on-top' if 'alwaysOnTop' in data and data['alwaysOnTop'] else ''} {f'--record={get_record_file_name(name)}' if record else ''} --window-title={name} --tcp={hostname}:{port}"

def show_help():
    help_text = """
    MOD+f
        Switch fullscreen mode

    MOD+Left
        Rotate display left

    MOD+Right
        Rotate display right

    MOD+g
        Resize window to 1:1 (pixel-perfect)

    MOD+w
    Double-click on black borders
        Resize window to remove black borders

    MOD+h
    Middle-click
        Click on HOME

    MOD+b
    MOD+Backspace
    Right-click (when screen is on)
        Click on BACK

    MOD+s
    4th-click
        Click on APP_SWITCH

    MOD+m
        Click on MENU

    MOD+Up
        Click on VOLUME_UP

    MOD+Down
        Click on VOLUME_DOWN

    MOD+p
        Click on POWER (turn screen on/off)

    Right-click (when screen is off)
        Power on

    MOD+o
        Turn device screen off (keep mirroring)

    MOD+Shift+o
        Turn device screen on

    MOD+r
        Rotate device screen

    MOD+n
    5th-click
        Expand notification panel

    MOD+Shift+n
        Collapse notification panel

    MOD+c
        Copy to clipboard (inject COPY keycode, Android >= 7 only)

    MOD+x
        Cut to clipboard (inject CUT keycode, Android >= 7 only)

    MOD+v
        Copy computer clipboard to device, then paste (inject PASTE keycode,
        Android >= 7 only)

    MOD+Shift+v
        Inject computer clipboard text as a sequence of key events

    MOD+i
        Enable/disable FPS counter (print frames/second in logs)

    Ctrl+click-and-move
        Pinch-to-zoom from the center of the screen

    Drag & drop APK file
        Install APK from computer

    Drag & drop non-APK file
        Push file to device (see --push-target)
    """

    help_layout = [[gui.Column([[gui.Text(help_text)]], scrollable=True, vertical_scroll_only=True)]]
    help_window = gui.Window(title="Help", layout=help_layout)
    help_window.read()
    help_window.close()

def make_pair_dialog(name, hostname):
    pair_layout = [
        [gui.Text(text="Pairing port", size=(20, 1)), gui.InputText(size=(50, 1))],
        [gui.Text(text="Pairing code", size=(20, 1)), gui.InputText(size=(50, 1))],
        [gui.Submit("Ok"), gui.Cancel("Cancel")]
    ]
    pair_window = gui.Window(title=f"Pair {name}", no_titlebar=True, keep_on_top=True, resizable=False, layout=pair_layout)
    ev, val = pair_window.read()
    if ev == "Ok":
        system(f"adb pair {hostname}:{val[0]} {val[1]}")
    pair_window.close()


commands = get_commands_existance()
missing_commands = [(c, e) for c, e in commands if(not e)]
if missing_commands:
    print("Missing commands:")
    print(missing_commands)
    exit()

data = get_data()

layout = make_layout(data)

window = make_window(layout)

cont = True

while cont:
    ev, vals = window.read()

    match ev:
        case gui.WIN_CLOSED:
            cont = False
        case "+":
            conn = make_connection()
            if conn is not None:
                window.close()
                data["connections"].append(conn)
                save_data(data)
                layout = make_layout(data)
                window = make_window(layout)
        case ("Connect", name, hostname, port) | ("Record", name, hostname, port):
            window.close()
            print(f"Connect to {name}, at {hostname}:{port}")
            system(make_scrcpy_command(name, hostname, port, data, ev[0] == "Record"))
            if "disconnectDebugger" in data and data["disconnectDebugger"]:
                system(f"adb disconnect {hostname}:{port}")
            layout = make_layout(data)
            window = make_window(layout)
        case "Delete", name:
            window.close()
            data["connections"] = [s for s in data["connections"] if s["name"] != name]
            save_data(data)
            layout = make_layout(data)
            window = make_window(layout)
        case "Settings":
            data = make_settings_gui(data)
        case "Help":
            show_help()
        case "Pair", name, hostname:
            make_pair_dialog(name, hostname)
