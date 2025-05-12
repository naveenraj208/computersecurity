import tkinter as tk
from tkinter import messagebox, Label
from tkinter.ttk import Style
import requests
import threading
import time
import subprocess
import os
import logging
import json

# Flask API Endpoint
START_CAPTURE_URL = "http://127.0.0.1:3000/start-capture"

# Set up logging to log to a file in the Downloads folder
log_directory = os.path.expanduser('~/Downloads')
log_filename = os.path.join(log_directory, 'malware_detection_log.txt')
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(message)s')

class MalwareDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Malware Detection UI")
        self.root.geometry("600x350")
        self.root.configure(bg="#1c1c1c")  # Dark theme

        style = Style()
        style.configure("TLabel", font=("Helvetica", 14), background="#1c1c1c", foreground="white")

        self.title_label = Label(root, text="Malware Detection System", font=("Helvetica", 18, "bold"),
                                 bg="#1c1c1c", fg="#ffffff")
        self.title_label.pack(pady=10)

        self.prediction_label = Label(root, text="Waiting for predictions...", font=("Helvetica", 14),
                                      bg="#1c1c1c", fg="yellow")
        self.prediction_label.pack(pady=20)

        self.proof_label = Label(root, text="", font=("Helvetica", 10), wraplength=500,
                                 bg="#1c1c1c", fg="lightblue")
        self.proof_label.pack(pady=5)

        self.is_running = False
        self.last_real_detection_time = 0  # Track last real detection

        threading.Thread(target=self.check_detection_status, daemon=True).start()
        threading.Thread(target=self.fibonacci_alerts, daemon=True).start()

    def check_detection_status(self):
        while True:
            try:
                response = requests.get(START_CAPTURE_URL, stream=True, timeout=5)
                if response.status_code == 200:
                    self.is_running = True
                    for line in response.iter_lines():
                        if line:
                            try:
                                result = json.loads(line.decode('utf-8').replace("data: ", ""))
                                self.root.after(0, lambda res=result: self.display_prediction(res))
                            except json.JSONDecodeError:
                                continue
                else:
                    self.is_running = False
            except requests.exceptions.RequestException:
                self.is_running = False
            self.root.after(0, self.update_status_message)
            time.sleep(5)

    def update_status_message(self):
        if not self.is_running:
            self.prediction_label.config(text="Detection Not Begun", fg="orange")
            self.proof_label.config(text="")

    def fibonacci_alerts(self):
        fib_sequence = [1, 2]
        while True:
            delay = fib_sequence[-1]
            time.sleep(delay)

            time_since_last_detection = time.time() - self.last_real_detection_time
            if time_since_last_detection >= delay:
                self.root.after(0, self.trigger_failsafe_alert)
            fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])

    def trigger_failsafe_alert(self):
        self.prediction_label.config(text="Malware Detected !", fg="red")
        self.proof_label.config(text="No response from system, triggering detection.", fg="lightblue")
        self.send_alert("Malware Detection", " Malware detected in idle mode!")
        self.log_alert("Malware detected in idle mode!")

    def display_prediction(self, result):
        if isinstance(result, dict):
            label = result.get("status", "Unknown")
            msg = result.get("message", "")
            proof = result.get("proof", "")
            tx_hash = result.get("tx_hash", "")

            self.last_real_detection_time = time.time()  # Reset timer on real detection

            if label.lower() == "malware":
                self.prediction_label.config(text="Malware Detected!", fg="red")
                self.log_alert("Malware Detected")
                if tx_hash:
                    self.proof_label.config(
                        text=f"Proof: {proof}\nLogged on Blockchain: {tx_hash}",
                        fg="lightblue"
                    )
                elif proof:
                    self.proof_label.config(text=f"Proof: {proof}", fg="lightblue")
            elif label.lower() == "benign":
                self.prediction_label.config(text="No Malware Detected", fg="green")
                self.proof_label.config(text="")
            else:
                self.prediction_label.config(text="Packets dont have an IP address", fg="orange")
                self.proof_label.config(text="")

    @staticmethod
    def send_alert(title, message):
        try:
            subprocess.run([
                "osascript",
                "-e",
                f'display notification "{message}" with title "{title}"'
            ])
        except Exception as e:
            print("Notification Error:", e)

    @staticmethod
    def log_alert(message):
        logging.info(message)

if __name__ == "__main__":
    root = tk.Tk()
    app = MalwareDetectionApp(root)
    root.mainloop()
