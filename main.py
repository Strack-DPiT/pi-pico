import utime
import _thread
import bluetooth
from ble_simple_peripheral import BLESimplePeripheral
import time
import json

userData = {"lat": 46.123, "long": 23.123, "user_id": "David"}
bluetooth_data = {
	"type": "u",
	"user_id": "",
	"lat": 43.123,
	"long": 23.123,
	"heard_devices": {
        "1": {
            "user_id": "",
            "lat": 43,
            "long": 23
        }
    }
}
lora_data=""

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
    bluetooth_data["lat"] = userData["lat"]
    bluetooth_data["long"] = userData["long]
    bluetooth_data["user_id"] = userData["user_id"]
    debounce_time = 0
    if (time.ticks_ms()-debounce_time) > 300:
        if sp.is_connected():
            bluetooth_data = json.dumps(userData)
            sp.send(bluetooth_data)
            print("BluetoothSent")
        debounce_time = time.ticks_ms()
        
def get_gps_data():
    userData["lat"] += 1
    userData["long"] += 1
    print("Gps Data updated", userData)

def parse_data():
    parsed_string = "L"
    if(len(userData["user_id"]) <= 8):
        parsed_string += userData["user_id"]
        number = 8 - len(userData["user_id"])
        parsed_string += "*" * number;
    parsed_string += str(userData["lat"])
    parsed_string += str(userData["long"])
    lora_data = parsed_string
    

def reverse_parse_data(lora_data):
    if lora_data[0] != 'L':
        raise ValueError("Invalid lora_data format")
    parsed_data = {"user_id": "", "lat": "", "long": ""}
    lora_data = lora_data[1:]
    for char in lora_data:
        if char == '*':
            break
        parsed_data["user_id"] += char
    lora_data = lora_data[len(parsed_data["user_id"]):]  # Remove the user_id and '*' characters
    if len(lora_data) < 2:
        raise ValueError("Invalid lora_data format")
    parsed_data["lat"] = lora_data[0]
    parsed_data["long"] = lora_data[1]

def lora_send():
    parse_data()
    print("lora data sent", lora_data)
    
def lora_receive():
    bluetooth_data["heard_devices"] = ""
    received_data = "LDavid***43.11123000"
    received_data = reverse_parse_data(received_data)
    bluetooth_data["heard_devices"].append(received_data)
    print(bluetooth_data)
    print("receive lora")
    ##utime.sleep_ms(25000)

getGpsData = Task("Gets gps data from gps module", 30000, get_gps_data)
loraSend = Task("Send the lora information", 30000, lora_send)
loraReceive = Task("Listen on Lora", 30000, lora_receive)
sendbluetooth_data = Task("Send Gps Data to Phone", 30000, send_bluetooth_data)

task_manager = TaskManager()
task_manager.add_task(getGpsData)
task_manager.add_task(loraSend)
task_manager.add_task(loraReceive)
task_manager.add_task(sendbluetooth_data)

task_manager.start()

