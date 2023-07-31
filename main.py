import utime
import _thread
import bluetooth
from ble_simple_peripheral import BLESimplePeripheral
import time
import json

gpsData = {"lat": 40, "long": 80}
bluetoothJson = "{}"


# Create a Bluetooth Low Energy (BLE) object
ble = bluetooth.BLE()
# Create an instance of the BLESimplePeripheral class with the BLE object
sp = BLESimplePeripheral(ble)

class Task:
    def __init__(self, name, interval, callback):
        self.name = name
        self.interval = interval
        self.callback = callback
        self.next_run = utime.ticks_ms() + interval

    def run(self):
        self.callback()
        self.next_run = utime.ticks_add(utime.ticks_ms(), self.interval)

class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def start(self):
        while True:
            now = utime.ticks_ms()
            for task in self.tasks:
                if utime.ticks_diff(task.next_run, now) <= 0:
                    task.run()
            utime.sleep_ms(50)  # Adjust this sleep value based on the desired resolution

def send_bluetooth_data():
    debounce_time = 0
    if (time.ticks_ms()-debounce_time) > 300:
        if sp.is_connected():
            bluetoothJson = json.dumps(gpsData)
            sp.send(bluetoothJson)
            print("BluetoothSent")
        debounce_time = time.ticks_ms()
        
def get_gps_data():
    gpsData["lat"] += 1
    gpsData["long"] += 1
    print("Gps Data updated", gpsData)

getGpsData = Task("Gets gps data from gps module", 30000, get_gps_data)
sendBluetoothData = Task("Send Gps Data to Phone", 10000, send_bluetooth_data)

task_manager = TaskManager()
task_manager.add_task(getGpsData)
task_manager.add_task(sendBluetoothData)

task_manager.start()
