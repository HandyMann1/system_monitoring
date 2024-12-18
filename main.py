import logging
import os
import time
from threading import Thread
import matplotlib.pyplot as plt

logging.basicConfig(filename='system_audit.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

process_counts = []
file_change_counts = []


def log_event(event):
    logging.info(event)
    print(event)


def monitor_processes():
    while True:
        processes = os.popen('ps aux').readlines()
        process_count = len(processes)
        process_counts.append(process_count)
        log_event(f'Process count: {process_count}')
        time.sleep(60)


def monitor_file_changes(path):
    file_mod_times = {}
    while True:
        file_change_count = 0
        log_event(f'Monitoring directory: {path}')
        for root, dirs, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                if os.path.exists(full_path):
                    try:
                        mod_time = os.path.getmtime(full_path)
                        if full_path not in file_mod_times:
                            file_mod_times[full_path] = mod_time
                        elif file_mod_times[full_path] != mod_time:
                            log_event(f'File changed: {full_path}')
                            log_event(f'ALERT: File changed: {full_path}')
                            file_mod_times[full_path] = mod_time
                            file_change_count += 1
                    except FileNotFoundError:
                        log_event(f'File not found when checking modification time: {full_path}')


        if file_change_count > 0:
            log_event(f'Total changes detected this cycle: {file_change_count}')
            file_change_counts.append(file_change_count)
        else:
            file_change_counts.append(0)

        time.sleep(60)


def plot_data():
    plt.ion()
    while True:
        time.sleep(60)

        plt.clf()

        plt.subplot(2, 1, 1)
        plt.plot(process_counts, label='Process Count', color='blue')
        plt.title('Process Count Over Time')
        plt.xlabel('Time (minutes)')
        plt.ylabel('Number of Processes')
        plt.legend()
        plt.grid()

        plt.subplot(2, 1, 2)
        plt.plot(file_change_counts, label='File Change Count', color='red')
        plt.title('File Change Count Over Time')
        plt.xlabel('Time (minutes)')
        plt.ylabel('Number of File Changes')
        plt.legend()
        plt.grid()

        plt.tight_layout()

        plt.pause(0.01)


if __name__ == "__main__":
    process_thread = Thread(target=monitor_processes)
    file_monitor_thread = Thread(target=monitor_file_changes,
                                 args=('/home',))

    process_thread.start()
    file_monitor_thread.start()

    plot_data()
