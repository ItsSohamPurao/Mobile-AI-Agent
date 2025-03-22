import subprocess

import subprocess

def get_battery_status():
    result = subprocess.run(["adb", "shell", "dumpsys battery"], capture_output=True, text=True)
    lines = result.stdout.split("\n")
    battery_info = {}
    
    for line in lines:
        parts = line.strip().split(": ")
        if len(parts) == 2:
            key, value = parts
            battery_info[key.strip()] = value.strip()
    
    return {
        "Level": battery_info.get("level", "N/A"),
        "Status": battery_info.get("status", "N/A"),
        "Temperature": battery_info.get("temperature", "N/A"),
        "Voltage": battery_info.get("voltage", "N/A"),
    }

print("Battery Status:", get_battery_status())


def get_ram_usage():
    result = subprocess.run(["adb", "shell", "dumpsys meminfo"], capture_output=True, text=True)
    lines = result.stdout.split("\n")
    for line in lines:
        if "Mem:" in line:  # Find the line with total RAM info
            parts = line.split()
            return {
                "Total_RAM": parts[1] + " KB",
                "Used_RAM": parts[3] + " KB",
                "Free_RAM": parts[5] + " KB",
            }
    return "N/A"

print("RAM Usage:", get_ram_usage())


def get_cpu_usage():
    result = subprocess.run(["adb", "shell", "top", "-n", "1"], capture_output=True, text=True)
    lines = result.stdout.split("\n")
    for line in lines:
        if "cpu" in line.lower():
            return line.strip()
    return "N/A"

print("CPU Usage:", get_cpu_usage())

