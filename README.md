# HideAndHide

HideAndHide is a dynamic auto-hide utility for [Waybar](https://github.com/Alexays/Waybar) when running on [Hyprland](https://github.com/hyprwm/Hyprland). It listens to your cursor's position via `hyprctl` and dynamically shows or hides your Waybar based on proximity to the screen edge. 

This repository contains two different versions to suit your needs:

## 1. HidePrototype.py (Lightweight Version)
The `HidePrototype` is a more lightweight and simpler version of the script. It is designed to be easy to use and understand while still being powerful.
- **Top-Bar Only:** It assumes a standard top-bar configuration, triggering Waybar when your cursor is near the top edge.
- **Multi-Monitor Support:** Correctly identifies which monitor your cursor is on and spawns Waybar specifically on that monitor.
- **Transformations Support:** Accounts for monitor rotation and scaling dynamically.
- Excellent if your bar is at the top and you just want a quick and easy solution.

## 2. HideAndHide.py (Extended Version)
The `HideAndHide` script is the full, extended version. It includes all the features of the prototype (like multi-monitor and transformations support) but adds advanced auto-detection capabilities:
- **Dynamic Position Detection:** It automatically reads your `~/.config/waybar/config.jsonc` to figure out if your bar is positioned at the `top`, `bottom`, `left`, or `right` and calculates proximity based on the correct screen edge.

## Configuration

Both scripts read their settings from `config.json` in the same directory:

```json
{
    "delay_in": 0.1,
    "delay_out": 0.5,
    "updating": 0.1,
    "distance_in": 10,
    "distance_out": 50
}
```

- `distance_in`: How close (in pixels) the cursor needs to be to the edge to trigger Waybar.
- `distance_out`: How far the cursor needs to be from the edge before Waybar is hidden.
- `delay_in`: Delay (in seconds) before Waybar is shown when the cursor enters the trigger zone.
- `delay_out`: Delay (in seconds) before Waybar is killed when the cursor leaves the trigger zone.
- `updating`: Polling rate for the cursor position.

## Dependencies
- Python 3
- `hyprctl` (Hyprland)
- `waybar`

## Usage
Simply run the version of the script you prefer in the background:
```bash
python3 HideAndHide.py &
# or
python3 HidePrototype.py &
```
