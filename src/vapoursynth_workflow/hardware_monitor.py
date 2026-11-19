import subprocess
import time
import json
import threading
import urllib.request
import psutil
import winsound

def get_cpu_temperature(node: dict) -> float:
    
    text = node.get("Text", "")
    value = node.get("Value", "")
    
    # Check if the node is a CPU Core and contains a temperature value
    if "CPU Core" in text and "°C" in value:
        clean_value = value.replace("°C", "").strip().replace(",", ".")
        return float(clean_value)
    
    # Recursively search in children nodes
    for child in node.get("Children", []):
        result = get_cpu_temperature(child)
        if result > 0: 
            return result
            
    return 0.0

def get_cpu_clock(node: dict) -> float:
    
    text = node.get("Text", "")
    value = node.get("Value", "")
    
    if "CPU Core" in text and "MHz" in value:
        # OHM formats like "2,666.0 MHz" -> Clean it up to "2666.0"
        clean_value = value.replace("MHz", "").strip().replace(",", "")
        return float(clean_value)
    
    # Recursively search in children nodes
    for child in node.get("Children", []):
        result = get_cpu_clock(child)
        if result > 0: 
            return result
            
    return 0.0

def monitor(p_vspipe: subprocess.Popen, p_nvencc: subprocess.Popen, stop_event: threading.Event):
    
    while not stop_event.is_set():
        try:
            try:
                response = urllib.request.urlopen("http://localhost:8085/data.json", timeout=1)
                ohm_data = json.loads(response.read().decode('utf-8'))
                cpu_temp = get_cpu_temperature(ohm_data)
                cpu_clock = get_cpu_clock(ohm_data)
            except Exception:
                cpu_temp = 0
                cpu_clock = 0
                
            gpu_temp_str = subprocess.getoutput("nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader")
            gpu_temp = int(gpu_temp_str.strip()) if gpu_temp_str.strip().isdigit() else 0
            
            cpu_load = psutil.cpu_percent(interval=1)
            ram_load = psutil.virtual_memory().percent
            
            # Base risk conditions
            hardware_risk = cpu_temp >= 92 or cpu_load >= 95 or gpu_temp >= 85 or ram_load >= 90
            
            # Thermal Throttling condition: High temp + drastic clock drop (under 1500 MHz)
            throttling_risk = (cpu_temp >= 88) and (0 < cpu_clock < 1500)
            
            if hardware_risk or throttling_risk:
                print(f"\n[WARNING] HARDWARE RISK DETECTED! Operation is being halted.")
                print(f"CPU: {cpu_temp}°C, CPU: %{cpu_load}, GPU: {gpu_temp}°C, RAM: %{ram_load}")
                winsound.Beep(1000, 2000)  # 2 sec alarm in 1000Hz frequency
                
                # terminate Popen processes immediately if they are still running.
                if p_vspipe.poll() is None:
                    p_vspipe.terminate()
                if p_nvencc.poll() is None:
                    p_nvencc.terminate()
                    
                stop_event.set()  # Break out of the loop to shut yourself down
                break
                
        except Exception as e:
            # Don't let the program crash if an intermittent API/WMI error occurs during reading
            print(f"[Monitör Error]: {e}")
            
        time.sleep(5)  # Check every 5 seconds.
