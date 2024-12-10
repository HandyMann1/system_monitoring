import os
import time
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(filename='system_audit.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# Функция для записи события в журнал
def log_event(event):
    logging.info(event)
    print(event)  # Выводим событие в консоль как внутреннее сообщение


# Функция для мониторинга процессов
def monitor_processes():
    while True:
        # Получаем список процессов
        processes = os.popen('ps aux').readlines()
        for process in processes:
            log_event(f'Process: {process.strip()}')
        time.sleep(60)  # Проверка каждые 60 секунд


# Функция для мониторинга изменений файлов
def monitor_file_changes(path):
    file_mod_times = {}
    while True:
        for root, dirs, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                mod_time = os.path.getmtime(full_path)
                if full_path not in file_mod_times:
                    file_mod_times[full_path] = mod_time
                elif file_mod_times[full_path] != mod_time:
                    log_event(f'File changed: {full_path}')
                    # Внутреннее сообщение о изменении файла
                    log_event(f'ALERT: File changed: {full_path}')
                    file_mod_times[full_path] = mod_time
        time.sleep(60)  # Проверка каждые 60 секунд


if __name__ == "__main__":
    # Запуск мониторинга процессов и изменений файлов в отдельных потоках (можно использовать threading или multiprocessing)
    from threading import Thread

    process_thread = Thread(target=monitor_processes)
    file_monitor_thread = Thread(target=monitor_file_changes,
                                 args=('/path/to/monitor',))  # Укажите путь для мониторинга

    process_thread.start()
    file_monitor_thread.start()
