import logging
import logging.config
from pythonjsonlogger import jsonlogger
import pandas as pd
import json
import matplotlib.pyplot as plt

# Настройка логирования с использованием JSON
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": "%(asctime)s %(levelname)s %(message)s",
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "system_audit.log",
            "formatter": "json",
        },
    },
    "loggers": {
        "my_logger": {
            "handlers": ["file"],
            "level": "DEBUG",
        },
    },
}

logging.config.dictConfig(LOGGING)
logger = logging.getLogger("my_logger")


# Функция для извлечения данных из лог-файла
def extract_log_data(log_file):
    log_entries = []

    with open(log_file, 'r') as file:
        for line in file:
            log_entries.append(json.loads(line.strip()))

    return pd.DataFrame(log_entries)


# Функция для анализа данных
def analyze_logs(df):
    # Подсчет количества логов по уровням
    level_counts = df['levelname'].value_counts()

    return level_counts


def plot_data(level_counts):
    # График количества событий по уровням логирования
    plt.figure(figsize=(12, 6))

    level_counts.plot(kind='bar', color='skyblue')
    plt.title('Количество событий по уровням логирования')
    plt.xlabel('Уровень логирования')
    plt.ylabel('Количество')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Извлечение и анализ данных из лог-файла
    log_df = extract_log_data('system_audit.log')

    level_counts = analyze_logs(log_df)

    # Визуализация данных
    plot_data(level_counts)
