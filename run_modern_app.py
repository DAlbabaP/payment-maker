#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Запуск PaymentMaker с современным интерфейсом
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в path
root_dir = Path(__file__).parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

def main():
    """Запускает приложение"""
    from PyQt6.QtWidgets import QApplication
    from paymentmaker.gui.modern_ui import ModernMainWindow
    from paymentmaker.utils.config import Config
    
    # Создаем приложение
    app = QApplication(sys.argv)
    app.setApplicationName("PaymentMaker")
    app.setOrganizationName("PaymentMaker")
    
    # Создаем конфигурацию
    config = Config()
    
    # Создаем и показываем главное окно
    window = ModernMainWindow(config)
    window.show()
    
    # Запускаем цикл событий
    sys.exit(app.exec())

if __name__ == "__main__":
    main()