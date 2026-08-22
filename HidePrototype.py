#!/usr/bin/env python3

import json, subprocess, os
import time

_cached_monitors = None
_last_monitors_update = 0

style_path = os.path.expanduser("~/.config/waybar/style.css")

with open("config.json", 'r', encoding='utf-8') as f:
    hide_config = json.load(f)

delay_in = hide_config.get("delay_in")
delay_out = hide_config.get("delay_out")
updating = hide_config.get("updating")
distance_in = hide_config.get("distance_in")
distance_out = hide_config.get("distance_out")

def get_cursor_position():
    output = subprocess.check_output(["hyprctl", "cursorpos"]).decode()
    x, y = output.split(",")
    return int(x), int(y)

def get_cached_monitors():
    global _cached_monitors, _last_monitors_update
    if time.time() - _last_monitors_update > 2 or not _cached_monitors:
        _cached_monitors = json.loads(subprocess.getoutput("hyprctl monitors -j"))
        _last_monitors_update = time.time()
    return _cached_monitors

def get_monitor():
    x, y = get_cursor_position()
    monitors = get_cached_monitors()
    for m in monitors:
        eff_width = m["height"] if m.get("transform", 0) % 2 != 0 else m["width"]
        eff_height = m["width"] if m.get("transform", 0) % 2 != 0 else m["height"]
        if m["x"] <= x < m["x"] + eff_width / m["scale"] and m["y"] <= y < m["y"] + eff_height / m["scale"]:
            return m["name"]
    return ""

def launch_waybar_on(monitor):
    raw = open(os.path.expanduser("~/.config/waybar/config.jsonc")).read()
    cfg = raw.replace("{", f'{{"output": "{monitor}",', 1)
    path = "/tmp/_waybar_cfg.json"
    open(path, "w").write(cfg)
    subprocess.Popen(["waybar", "-c", path, "-s", style_path])

last_x, last_y = None, None
visibility = 0

try:
    while True:
        x, y = get_cursor_position()
        if y <= distance_in and visibility == 0:
            mon = get_monitor()
            launch_waybar_on(mon)
            visibility = 1
            time.sleep(delay_in)
        elif y >= distance_out and visibility == 1:
            time.sleep(delay_out)
            subprocess.run(["killall", "waybar"])
            visibility = 0
        time.sleep(updating)
except KeyboardInterrupt:
    print("Stopped")
