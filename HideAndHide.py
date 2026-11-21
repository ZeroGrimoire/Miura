from pathlib import Path
import json, subprocess, os, re
import time

config_path = os.path.expanduser("~/.config/waybar/config.jsonc")
style_path = os.path.expanduser("~/.config/waybar/style.css")

script_dir = Path(__file__).resolve().parent

config_path = script_dir / "config.json"

with open(config_path, 'r', encoding='utf-8') as f:
    hide_config = json.load(f)

delay_in = hide_config.get("delay_in")
delay_out = hide_config.get("delay_out")
updating = hide_config.get("updating")
distance_in = hide_config.get("distance_in")
distance_out = hide_config.get("distance_out")

_cached_monitors = None
_last_monitors_update = 0

def get_cached_monitors():
    global _cached_monitors, _last_monitors_update
    if time.time() - _last_monitors_update > 2 or not _cached_monitors:
        _cached_monitors = json.loads(subprocess.getoutput("hyprctl monitors -j"))
        _last_monitors_update = time.time()
    return _cached_monitors

def start_waybar(direction, distanceIn, distanceOut):
    global visibility
    try:
            x, y = get_cursor_position()
            
            if direction in ["top", "bottom"]:
                pos = y
            else:
                pos = x
                
            print(x, y)
            if pos <= distanceIn and visibility == 0:
                mon = get_monitor()
                launch_waybar_on(mon)
                visibility = 1
                print(get_monitor())
                time.sleep(delay_in)
            elif pos >= distanceOut and visibility == 1:
                time.sleep(delay_out)
                subprocess.run(["killall", "waybar"])
                visibility = 0
            time.sleep(updating)
    except KeyboardInterrupt:
        print("Stopped")

def start_waybar_plus(direction, distanceIn, distanceOut):
    global visibility
    try:
            x, y = get_cursor_position()
            
            if direction in ["top", "bottom"]:
                pos = y
            else:
                pos = x
                
            print(x, y)
            if pos >= distanceIn and visibility == 0:
                mon = get_monitor()
                launch_waybar_on(mon)
                visibility = 1
                print(get_monitor())
                time.sleep(delay_in)
            elif pos <= distanceOut and visibility == 1:
                time.sleep(delay_out)
                subprocess.run(["killall", "waybar"])
                visibility = 0
            time.sleep(updating)
    except KeyboardInterrupt:
        print("Stopped")

def monitor_size(direction):
    monitors = get_cached_monitors()
    target = get_monitor()
    for m in monitors:
        if m["name"] == target:
            if m.get("transform", 0) % 2 != 0:
                return m["height"] if direction == "width" else m["width"]
            return m[direction]
    return 0

def monitor_edge(edge):
    monitors = get_cached_monitors()
    target = get_monitor()
    for m in monitors:
        if m["name"] == target:
            eff_width = m["height"] if m.get("transform", 0) % 2 != 0 else m["width"]
            eff_height = m["width"] if m.get("transform", 0) % 2 != 0 else m["height"]
            if edge == "top":
                return m["y"]
            elif edge == "bottom":
                return m["y"] + eff_height
            elif edge == "left":
                return m["x"]
            elif edge == "right":
                return m["x"] + eff_width
    return 0

def get_waybar_position():
    with open(config_path, "r") as f:
        match = re.search(r'"position"\s*:\s*"([^"]+)"', f.read())
    return match.group(1) if match else None

def get_cursor_position():
    output = subprocess.check_output(["hyprctl", "cursorpos"]).decode()
    x, y = output.split(",")
    return int(x), int(y)

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
    raw = open(config_path).read()
    cfg = raw.replace("{", f'{{"output": "{monitor}",', 1)
    path = "/tmp/_waybar_cfg.json"
    open(path, "w").write(cfg)
    subprocess.Popen(["waybar", "-c", path, "-s", style_path])

print("Listening for mouse position...")

last_x, last_y = None, None
visibility = 0

if get_waybar_position() == "top":
    while True:
        start_waybar("top", distance_in, distance_out)
elif get_waybar_position() == "bottom":
    while True:
        start_waybar_plus("bottom", monitor_edge("bottom") - distance_in, monitor_edge("bottom") - distance_out)
elif get_waybar_position() == "left":
    while True:
        start_waybar("left", distance_in, distance_out)
elif get_waybar_position() == "right":
    while True:
        start_waybar_plus("right", monitor_edge("right") - distance_in, monitor_edge("right") - distance_out)