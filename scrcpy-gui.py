import PySimpleGUI as gui
import json
from os import path

database_file = "db.json"

def make_window(layout):
    return gui.Window(title="Test", layout=layout, resizable=True)

def make_empty_db_data():
    return {
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
        [gui.Button(button_text="+", size=(2, 1))]
    ]
    for connection in data["connections"]:
        l.append([gui.Text(connection["name"]), gui.Button(">", size=(2, 1))])
    return l

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
            window.close()
            data["connections"].append({ "name": "Test" })
            save_data(data)
            layout = make_layout(data)
            window = make_window(layout)