"""
PaymentMaker - основной модуль приложения
"""

import sys
import os
import logging
from pathlib import Path

# Настройка путей
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
RESOURCES_DIR = ROOT_DIR / "resources"

# Создаем необходимые директории
DATA_DIR.mkdir(exist_ok=True)
(DATA_DIR / "input").mkdir(exist_ok=True)
(DATA_DIR / "output").mkdir(exist_ok=True)

# Настройка логирования
LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "paymentmaker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Главная функция приложения"""
    try:
        from PyQt6.QtWidgets import QApplication
        from paymentmaker.gui.main_window import PaymentMakerApp
        from paymentmaker.utils.config import Config
        
        # Загружаем конфигурацию
        config = Config()
        
        # Создаем приложение
        app = QApplication(sys.argv)
        app.setApplicationName("PaymentMaker")
        app.setOrganizationName("PaymentMaker")
        
        # Создаем и показываем главное окно
        window = PaymentMakerApp(config)
        window.show()
        
        logger.info("Приложение PaymentMaker запущено")
        return app.exec()
        
    except ImportError as e:
        logger.error(f"Не удалось загрузить необходимые модули: {e}")
        print(f"Ошибка: {e}")
        print("Установите все зависимости: pip install -r requirements.txt")
        return 1
    except Exception as e:
        logger.exception(f"Критическая ошибка: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())