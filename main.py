import logging
import logging.config
import os
import time
from threading import Thread
import matplotlib.pyplot as plt
from pythonjsonlogger import jsonlogger
import psutil

# Define custom log levels for different operations
PROCESS_STARTED = 25
PROCESS_ENDED = 30
FILE_CHANGED = 35
NETWORK_ACTIVITY = 40

# Add custom levels to the logging module
logging.addLevelName(PROCESS_STARTED, "PROCESS_STARTED")
logging.addLevelName(PROCESS_ENDED, "PROCESS_ENDED")
logging.addLevelName(FILE_CHANGED, "FILE_CHANGED")
logging.addLevelName(NETWORK_ACTIVITY, "NETWORK_ACTIVITY")

# Create a custom logger class to handle the new log levels
class CustomLogger(logging.Logger):
    def __init__(self, name):
        super().__init__(name)

    def process_started(self, message, *args, **kwargs):
        self.log(PROCESS_STARTED, message, *args, **kwargs)

    def process_ended(self, message, *args, **kwargs):
        self.log(PROCESS_ENDED, message, *args, **kwargs)

    def file_changed(self, message, *args, **kwargs):
        self.log(FILE_CHANGED, message, *args, **kwargs)

    def network_activity(self, message, *args, **kwargs):
        self.log(NETWORK_ACTIVITY, message, *args, **kwargs)

# Configure logging with multiple levels and handlers
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": "%(asctime)s %(levelname)s %(message)s",
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
        },
        "verbose": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "file_info": {
            "class": "logging.FileHandler",
            "filename": "system_audit.log",  # Change filename here
            "formatter": "json",               # Use JSON formatter for this handler
            "level": "DEBUG",                  # Set level to DEBUG to capture all logs including custom levels
        },
        "console_warning": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "level": "WARNING",
        },
    },
    "loggers": {
        # Set logger level to DEBUG to capture all custom levels and INFO logs
        "system_audit_logger": {
            "handlers": ["file_info", "console_warning"],
            # Set level to DEBUG; this will include all custom levels above INFO
            "level": "DEBUG",
        },
    },
}

# Set the custom logger class before creating the logger instance
logging.setLoggerClass(CustomLogger)
logging.config.dictConfig(LOGGING)

logger = logging.getLogger("system_audit_logger")

process_counts = []
file_change_counts = []

def log_event(event_type, message):
    if event_type == 'process_started':
        logger.process_started(message)
    elif event_type == 'process_ended':
        logger.process_ended(message)
    elif event_type == 'file_changed':
        logger.file_changed(message)
    elif event_type == 'network_activity':
        logger.network_activity(message)

def monitor_processes():
    previous_processes = {p.pid: p.info for p in psutil.process_iter(['pid', 'name'])}

    while True:
        current_processes = {p.pid: p.info for p in psutil.process_iter(['pid', 'name'])}

        new_processes = set(current_processes) - set(previous_processes)
        for pid in new_processes:
            log_event('process_started', f'Process started: {current_processes[pid]["name"]} (PID: {pid})')

        terminated_processes = set(previous_processes) - set(current_processes)
        for pid in terminated_processes:
            log_event('process_ended', f'Process ended: {previous_processes[pid]["name"]} (PID: {pid})')

        process_count = len(current_processes)
        process_counts.append(process_count)

        logger.info(f'Current process count: {process_count}')  # General info about process count

        previous_processes = current_processes
        time.sleep(60)

def monitor_file_changes(path):
    file_mod_times = {}

    while True:
        file_change_count = 0
        log_event('file_changed', f'Monitoring directory: {path}')

        for root, dirs, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                if os.path.exists(full_path):
                    try:
                        mod_time = os.path.getmtime(full_path)
                        if full_path not in file_mod_times:
                            file_mod_times[full_path] = mod_time
                        elif file_mod_times[full_path] != mod_time:
                            log_event('file_changed', f'File changed: {full_path}')
                            logger.info(f'ALERT: File changed: {full_path}')  # Log alert separately if needed
                            file_mod_times[full_path] = mod_time
                            file_change_count += 1
                    except FileNotFoundError:
                        log_event('file_changed', f'File not found when checking modification time: {full_path}')

        if file_change_count > 0:
            logger.info(f'Total changes detected this cycle: {file_change_count}')  # General info about changes
            file_change_counts.append(file_change_count)

        time.sleep(60)

def monitor_network_activity():
    while True:
        net_io = psutil.net_io_counters()
        log_event('network_activity', f'Sent bytes: {net_io.bytes_sent}, Received bytes: {net_io.bytes_recv}')

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
    file_monitor_thread = Thread(target=monitor_file_changes, args=('/home',))
    network_monitor_thread = Thread(target=monitor_network_activity)

    process_thread.start()
    file_monitor_thread.start()
    network_monitor_thread.start()

    plot_data()
