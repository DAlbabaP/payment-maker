"""
Современный интерфейс для PaymentMaker с Material Design
"""

import sys
import os
import re
import subprocess  # Добавлен импорт для печати
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from decimal import Decimal, InvalidOperation

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox,
    QProgressBar, QGroupBox, QFrame, QDateEdit,
    QTableView, QHeaderView, QDialog, QGraphicsDropShadowEffect,
    QComboBox, QListWidget, QListWidgetItem, QAbstractItemView,
    QMenu, QSystemTrayIcon, QStyle, QSplitter, QTextEdit,
    QGraphicsOpacityEffect, QApplication
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QDate, QPropertyAnimation, 
    QEasingCurve, QPoint, QRect, QTimer, QAbstractTableModel,
    QModelIndex, QParallelAnimationGroup, QSequentialAnimationGroup,
    pyqtProperty, QSize
)
from PyQt6.QtGui import (
    QFont, QIcon, QPalette, QColor, QPixmap, QPainter,
    QBrush, QPen, QFontDatabase, QDragEnterEvent, QDropEvent,
    QLinearGradient, QAction
)

from paymentmaker.core.data_processor import DataProcessor
from paymentmaker.core.document_generator import DocumentGenerator
from paymentmaker.core.models import InvoiceData, TransportService
from paymentmaker.utils.config import Config
from paymentmaker.gui.modern_styles import ModernStyle
from paymentmaker.gui.modern_widgets import ModernButton, FileDropZone


class ModernTableModel(QAbstractTableModel):
    """Модель для современной таблицы с возможностью редактирования"""
    
    def __init__(self, services: List[TransportService] = None):
        super().__init__()
        self.services = services or []
        self.headers = ["№", "Описание", "Кол-во", "Ед.", "Цена", "Сумма"]
        self._theme = ModernStyle.get_theme()
    
    @property
    def theme(self):
        return self._theme
    
    @theme.setter
    def theme(self, value):
        self._theme = value
        self.layoutChanged.emit()
    
    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.services)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.headers)
    
    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        
        service = self.services[index.row()]
        col = index.column()
        
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            if col == 0:
                return index.row() + 1
            elif col == 1:
                # Для отображения используем краткое описание без перегруза информацией
                if role == Qt.ItemDataRole.DisplayRole:
                    # Формируем более короткую версию с переносами для отображения
                    date_str = service.date.strftime("%d.%m.%Y")
                    driver_name = service.driver_name[:20] + "..." if len(service.driver_name) > 20 else service.driver_name
                    car_number = service.car_number
                    route_str = " - ".join(service.route)
                    if len(route_str) > 40:
                        route_str = route_str[:37] + "..."
                    
                    return f"Транспортные услуги {date_str}\nводит. {driver_name}\nа/м Газель {car_number}\nмаршрут {route_str}"
                else:
                    # Для редактирования возвращаем полное описание
                    return service.description
            elif col == 2:
                return service.quantity
            elif col == 3:
                return service.unit
            elif col == 4:
                return float(service.price) if role == Qt.ItemDataRole.EditRole else f"{service.price:,.2f}"
            elif col == 5:
                return float(service.amount) if role == Qt.ItemDataRole.EditRole else f"{service.amount:,.2f}"
        
        elif role == Qt.ItemDataRole.ForegroundRole:
            # Красный цвет для неизвестных маршрутов
            if col == 1 and "Неизвестный" in str(service.route):
                return QColor(self._theme['error'])
            return QColor(self._theme['text_primary'])
        
        elif role == Qt.ItemDataRole.BackgroundRole:
            # Дополнительно подсвечиваем фон ячейки с неизвестным пунктом
            if col == 1 and "Неизвестный" in str(service.route):
                # Светло-красный фон
                return QColor(255, 235, 235)
            return None
        
        elif role == Qt.ItemDataRole.FontRole:
            font = QFont("Segoe UI", 11)
            if col == 0:
                font.setBold(True)
            # Делаем шрифт жирным для ячеек с неизвестным пунктом
            if col == 1 and "Неизвестный" in str(service.route):
                font.setBold(True)
            return font
        
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            # Выравнивание текста
            if col == 1:  # Описание - по левому краю с переносом строк
                return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            elif col in [0, 2, 3]:  # №, Кол-во, Ед. - по центру
                return int(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            else:  # Цена, Сумма - по правому краю
                return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section]
        return None
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """Определяет флаги для ячеек (редактируемость)"""
        flags = super().flags(index)
        if not index.isValid():
            return flags
        
        # Делаем столбцы редактируемыми, кроме номера и суммы
        col = index.column()
        if col in [1, 2, 3, 4]:  # Описание, количество, единица, цена
            return flags | Qt.ItemFlag.ItemIsEditable
            
        return flags
    
    def setData(self, index: QModelIndex, value, role=Qt.ItemDataRole.EditRole) -> bool:
        """Устанавливает отредактированные данные"""
        if not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False
            
        row = index.row()
        col = index.column()
        
        try:
            service = self.services[row]
            
            if col == 1:  # Описание
                # Используем прямое присваивание атрибуту вместо свойства
                service._description = str(value)  # Прямой доступ к атрибуту
                # Обновляем маршрут если описание изменилось
                if "маршрут" in str(value):
                    parts = str(value).split("маршрут")
                    if len(parts) > 1:
                        try:
                            route_str = parts[1].strip()
                            if route_str:
                                service.route = [s.strip() for s in route_str.split("-")]
                        except:
                            pass
            elif col == 2:  # Количество
                try:
                    quantity = int(value)
                    service.quantity = quantity
                    # Пересчитываем сумму
                    service.amount = service.price * service.quantity
                except (ValueError, TypeError):
                    return False
            elif col == 3:  # Единица измерения
                service.unit = str(value)
            elif col == 4:  # Цена
                try:
                    from decimal import Decimal
                    price = Decimal(str(value))
                    service.price = price
                    # Пересчитываем сумму
                    service.amount = service.price * service.quantity
                except (ValueError, TypeError, InvalidOperation):
                    return False
                    
            self.dataChanged.emit(index, index)
            
            # Если изменились цена или количество, нужно обновить сумму
            if col in [2, 4]:
                sum_index = self.index(row, 5)
                self.dataChanged.emit(sum_index, sum_index)
                
            return True
        except Exception as e:
            print(f"Ошибка при редактировании: {e}")
            return False
    
    def update_services(self, services: List[TransportService]):
        self.beginResetModel()
        self.services = services
        self.endResetModel()


class ModernMainWindow(QMainWindow):
    """Главное окно с современным интерфейсом"""
    
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.current_theme = 'light'
        self.theme = ModernStyle.get_theme(self.current_theme)
        self.current_services = []
        self.recent_files = []
        self.current_file = None
        self.last_generated_file = None  # Для хранения пути последнего сгенерированного файла
        self.setup_ui()
        self.load_recent_files()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    
    def paintEvent(self, event):
        """Переопределяем отрисовку фона главного окна"""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(self.theme['bg_primary']))
        super().paintEvent(event)
    
    def setup_ui(self):
        self.setWindowTitle("PaymentMaker")
        self.setMinimumSize(1200, 800)
        
        # Устанавливаем современный шрифт
        self.setFont(QFont("Segoe UI", 10))
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {self.theme['bg_primary']};
                color: {self.theme['text_primary']};
            }}
        """)
        
        # Основной макет
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Создаем элементы интерфейса
        self.create_header()
        main_layout.addWidget(self.header)
        
        # Контентная область с отступами
        content_widget = QWidget()
        content_widget.setStyleSheet(f"background-color: {self.theme['bg_primary']};")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(32, 32, 32, 32)
        content_layout.setSpacing(24)
        
        self.create_file_section(content_layout)
        self.create_data_section(content_layout)
        self.create_actions_section(content_layout)
        
        main_layout.addWidget(content_widget, 1)
        
        # Применяем тему
        self.apply_theme()
    
    def create_header(self):
        """Создает современный заголовок"""
        self.header = QWidget()
        self.header.setFixedHeight(80)
        self.header.setStyleSheet(f"""
            QWidget {{
                background-color: {self.theme['bg_secondary']};
                border-bottom: 1px solid {self.theme['border']};
            }}
        """)
        
        layout = QHBoxLayout(self.header)
        layout.setContentsMargins(32, 0, 32, 0)
        
        # Логотип и название
        title_label = QLabel("PaymentMaker")
        title_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 600;
            color: {self.theme['text_primary']};
        """)
        
        subtitle_label = QLabel("Создание счетов и актов")
        subtitle_label.setStyleSheet(f"""
            font-size: 14px;
            color: {self.theme['text_secondary']};
        """)
        
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # Кнопки в заголовке
        self.settings_btn = ModernButton("⚙️ Настройки")
        self.settings_btn.clicked.connect(self.open_settings)
        
        self.theme_btn = ModernButton("🌙" if self.current_theme == 'light' else "☀️")
        self.theme_btn.clicked.connect(self.toggle_theme)
        
        layout.addWidget(self.settings_btn)
        layout.addWidget(self.theme_btn)
    
    def create_file_section(self, layout):
        """Создает секцию выбора файлов"""
        # Карточка для файлов
        file_card = self.create_card("Выбор файла")
        file_layout = file_card.layout()
        
        # Drag & Drop зона
        self.drop_zone = FileDropZone()
        self.drop_zone.fileDropped.connect(self.load_file)
        file_layout.addWidget(self.drop_zone)
        
        # История файлов
        history_label = QLabel("Недавние файлы:")
        history_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 500;
            color: {self.theme['text_secondary']};
            margin-top: 16px;
        """)
        file_layout.addWidget(history_label)
        
        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(120)
        self.recent_list.setStyleSheet(ModernStyle.get_list_widget_style(self.theme))
        self.recent_list.itemClicked.connect(self.load_recent_file)
        file_layout.addWidget(self.recent_list)
        
        layout.addWidget(file_card)
    
    def create_data_section(self, layout):
        """Создает секцию с данными"""
        # Карточка для параметров
        params_card = self.create_card("Параметры документа")
        params_layout = params_card.layout()
        
        # Горизонтальный макет для полей
        fields_layout = QHBoxLayout()
        fields_layout.setSpacing(32)
        
        # Номер счета
        invoice_group = QVBoxLayout()
        invoice_label = QLabel("Номер счета:")
        invoice_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 500;
            color: {self.theme['text_secondary']};
        """)
        
        self.invoice_number = QLineEdit()
        self.invoice_number.setText("001")
        self.invoice_number.setStyleSheet(ModernStyle.get_input_style(self.theme))
        self.invoice_number.setMaximumWidth(200)
        
        invoice_group.addWidget(invoice_label)
        invoice_group.addWidget(self.invoice_number)
        
        # Дата счета
        date_group = QVBoxLayout()
        date_label = QLabel("Дата счета:")
        date_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 500;
            color: {self.theme['text_secondary']};
        """)
        
        self.invoice_date = QDateEdit()
        self.invoice_date.setDate(QDate.currentDate())
        self.invoice_date.setCalendarPopup(True)
        self.invoice_date.setDisplayFormat("dd MMMM yyyy")
        self.invoice_date.setStyleSheet(ModernStyle.get_date_edit_style(self.theme))
        self.invoice_date.setMaximumWidth(250)
        
        date_group.addWidget(date_label)
        date_group.addWidget(self.invoice_date)
        
        fields_layout.addLayout(invoice_group)
        fields_layout.addLayout(date_group)
        fields_layout.addStretch()
        
        params_layout.addLayout(fields_layout)
        layout.addWidget(params_card)
        
        # Статус обработки
        self.status_card = self.create_card("Статус")
        status_layout = self.status_card.layout()
        
        self.status_label = QLabel("Готов к работе")
        self.status_label.setStyleSheet(f"""
            font-size: 16px;
            color: {self.theme['text_secondary']};
        """)
        status_layout.addWidget(self.status_label)
        
        self.status_card.hide()
        layout.addWidget(self.status_card)
    
    def create_actions_section(self, layout):
        """Создает секцию действий"""
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 32, 0, 0)
        
        self.preview_btn = ModernButton("Предпросмотр")
        self.preview_btn.clicked.connect(self.preview_data)
        self.preview_btn.setEnabled(False)
        
        self.generate_btn = ModernButton("Создать документы", primary=True)
        self.generate_btn.clicked.connect(self.generate_documents)
        self.generate_btn.setEnabled(False)
        
        self.print_btn = ModernButton("🖨️ Печать")
        self.print_btn.clicked.connect(self.print_documents)
        self.print_btn.setEnabled(False)
        
        actions_layout.addWidget(self.preview_btn)
        actions_layout.addWidget(self.generate_btn)
        actions_layout.addWidget(self.print_btn)
        actions_layout.addStretch()
        
        layout.addWidget(actions_widget)
    

    
    def create_card(self, title):
        """Создает карточку с заголовком"""
        card = QFrame()
        card.setObjectName(f"card_{title}")  # Устанавливаем имя объекта
        card.setStyleSheet(ModernStyle.get_card_style(self.theme))
        
        # Добавляем тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setOffset(0, 4)
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(0, 0, 0, 20))
        card.setGraphicsEffect(shadow)
        
        # Создаем макет
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        
        # Заголовок карточки
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 600;
            color: {self.theme['text_primary']};
            margin-bottom: 16px;
        """)
        card_layout.addWidget(title_label)
        
        return card
    
    def toggle_theme(self):
        """Переключение темы с отладкой"""
        print(f"Текущая тема: {self.current_theme}")
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        print(f"Новая тема: {self.current_theme}")
        self.theme = ModernStyle.get_theme(self.current_theme)
        print(f"Цвет фона: {self.theme['bg_primary']}")
        self.theme_btn.setText("☀️" if self.current_theme == 'dark' else "🌙")
        self.apply_theme()
        
        # Дополнительное обновление для проблемных элементов
        QTimer.singleShot(100, self._post_theme_update)

    def _post_theme_update(self):
        """Дополнительное обновление после смены темы"""
        # Обновляем все виджеты еще раз
        for widget in self.findChildren(QWidget):
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()
    
    def apply_theme(self):
        self.setStyleSheet("")
        QApplication.processEvents()
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.theme['bg_primary']};
            }}
        """)
        
        # Затем обновляем центральный виджет
        self.centralWidget().setStyleSheet(f"""
            QWidget {{
                background-color: {self.theme['bg_primary']};
                color: {self.theme['text_primary']};
            }}
        """)
        """Применение темы с детальным обновлением"""
        # Базовый стиль для всего окна
        base_style = f"""
            * {{
                background-color: {self.theme['bg_primary']};
                color: {self.theme['text_primary']};
            }}
            QMainWindow {{
                background-color: {self.theme['bg_primary']};
            }}
            QWidget {{
                background-color: transparent;
                color: {self.theme['text_primary']};
            }}
        """
        self.setStyleSheet(base_style)
        
        # Обновляем центральный виджет явно
        self.centralWidget().setStyleSheet(f"""
            background-color: {self.theme['bg_primary']};
            color: {self.theme['text_primary']};
        """)
        
        # Обновляем header явно
        self.header.setStyleSheet(f"""
            QWidget {{
                background-color: {self.theme['bg_secondary']};
                border-bottom: 1px solid {self.theme['border']};
                color: {self.theme['text_primary']};
            }}
        """)
        
        # Обновляем все QFrame (карточки)
        for frame in self.findChildren(QFrame):
            if frame.objectName() == 'FileDropZone':
                continue  # Особая обработка для FileDropZone
            
            frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.theme['bg_secondary']};
                    border-radius: 12px;
                    border: 1px solid {self.theme['border']};
                }}
            """)
            
            # Обновляем все дочерние элементы карточки
            for child in frame.findChildren(QWidget):
                if isinstance(child, QLabel):
                    child.setStyleSheet(f"""
                        background-color: transparent;
                        color: {self.theme['text_primary']};
                    """)
        
        # Обновляем все метки
        for label in self.findChildren(QLabel):
            current_style = label.styleSheet()
            # Сохраняем размер шрифта, но обновляем цвета
            if 'font-size' in current_style:
                font_size_match = re.search(r'font-size:\s*(\d+px);', current_style)
                if font_size_match:
                    font_size = font_size_match.group(1)
                    label.setStyleSheet(f"""
                        font-size: {font_size};
                        color: {self.theme['text_primary']};
                        background-color: transparent;
                    """)
            else:
                label.setStyleSheet(f"""
                    color: {self.theme['text_primary']};
                    background-color: transparent;
                """)
        
        # Обновляем все кнопки
        for button in self.findChildren(ModernButton):
            button.theme = self.theme
            button.setup_style()
        
        # Обновляем поля ввода
        self.invoice_number.setStyleSheet(ModernStyle.get_input_style(self.theme))
        self.invoice_date.setStyleSheet(ModernStyle.get_date_edit_style(self.theme))
        
        # Обновляем список файлов
        self.recent_list.setStyleSheet(ModernStyle.get_list_widget_style(self.theme))
        
        # Обновляем FileDropZone
        if hasattr(self, 'drop_zone'):
            self.drop_zone.theme = self.theme
            self.drop_zone.update_style()
            # Обновляем внутренние элементы
            for label in self.drop_zone.findChildren(QLabel):
                label.setStyleSheet(f"""
                    color: {self.theme['text_secondary']};
                    background-color: transparent;
                """)
        
        # Обновляем статус карточку
        if hasattr(self, 'status_card'):
            self.status_card.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.theme['bg_secondary']};
                    border-radius: 12px;
                    border: 1px solid {self.theme['border']};
                }}
            """)
            if hasattr(self, 'status_label'):
                self.status_label.setStyleSheet(f"""
                    font-size: 16px;
                    color: {self.theme['text_secondary']};
                    background-color: transparent;
                """)
        
        # Принудительное обновление
        self.update()
        self.repaint()
        QApplication.processEvents()

        for widget in self.findChildren(QWidget):
            if hasattr(widget, 'theme'):
                widget.theme = self.theme
                if hasattr(widget, 'update_style'):
                    widget.update_style()
                if hasattr(widget, 'setup_style'):
                    widget.setup_style()
    
    def show_preview_dialog(self, services):
        """Показывает диалог предпросмотра с возможностью редактирования"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Предпросмотр данных")
        dialog.setMinimumSize(900, 700)  # Увеличены размеры для лучшего отображения
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {self.theme['bg_primary']};
            }}
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Заголовок
        title = QLabel("Предпросмотр обработанных данных")
        title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 600;
            color: {self.theme['text_primary']};
            margin-bottom: 16px;
        """)
        layout.addWidget(title)
        
        # Инструкция по редактированию
        edit_instructions = QLabel("Для редактирования дважды щелкните по ячейке. Можно изменять описание, количество, единицы и цену.")
        edit_instructions.setStyleSheet(f"""
            font-size: 14px;
            font-style: italic;
            color: {self.theme['text_secondary']};
            margin-bottom: 8px;
        """)
        layout.addWidget(edit_instructions)
        
        # Таблица
        table = QTableView()
        model = ModernTableModel(services)
        model.theme = self.theme  # Устанавливаем тему для модели
        table.setModel(model)
        table.setStyleSheet(f"""
            QTableView {{
                background-color: {self.theme['bg_secondary']};
                border: 1px solid {self.theme['border']};
                border-radius: 8px;
                gridline-color: {self.theme['border']};
                color: {self.theme['text_primary']};
            }}
            QTableView::item {{
                padding: 8px;
                border-bottom: 1px solid {self.theme['border']};
            }}
            QTableView::item:selected {{
                background-color: {self.theme['accent']};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {self.theme['bg_secondary']};
                color: {self.theme['text_primary']};
                padding: 12px;
                border: none;
                font-weight: 600;
            }}
            /* Стиль для описания */
            QTableView::item:!selected:!focus {{
                color: {self.theme['text_primary']};
            }}
        """)
        table.horizontalHeader().setStretchLastSection(False)
        table.verticalHeader().setVisible(False)
        
        # Настройка редактирования
        table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | 
                             QAbstractItemView.EditTrigger.EditKeyPressed)
        
        # Автоматическая настройка ширины столбцов
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Описание растягивается
        
        # Включаем перенос текста и устанавливаем высоту строк
        table.setWordWrap(True)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        
        # Устанавливаем фиксированную высоту строк
        for row in range(len(services)):
            table.setRowHeight(row, 100)  # Увеличенная высота для многострочного текста
        
        layout.addWidget(table, 1)  # Растягиваем таблицу
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        # Кнопка сохранения изменений
        save_btn = ModernButton("Сохранить изменения")
        save_btn.theme = self.theme
        save_btn.clicked.connect(lambda: self.save_preview_changes(model.services, dialog))
        
        close_btn = ModernButton("Закрыть", primary=True)
        close_btn.theme = self.theme
        close_btn.clicked.connect(dialog.accept)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_btn)
        layout.addLayout(buttons_layout)
        
        # Запускаем диалог
        result = dialog.exec()
    
    def save_preview_changes(self, edited_services, dialog=None):
        """Сохраняет изменения из предпросмотра"""
        self.current_services = edited_services.copy()  # Создаем копию, чтобы избежать проблем с ссылками
        self.show_notification("Изменения сохранены", "success")
        
        # Если диалог передан, закрываем его после сохранения
        if dialog:
            dialog.accept()
    
    def extract_date_from_filename(self, filename):
        """Извлекает дату из имени файла
        
        Ищет упоминания месяцев и диапазона дат в формате "Месяц X-Y"
        Например: "Апрель 16-30", "Май 1-15" и т.д.
        """
        filename = Path(filename).stem  # Берем только имя файла без расширения
        
        # Словарь месяцев на русском и соответствующий номер месяца
        months = {
            'январ': 1, 'февр': 2, 'март': 3, 'апрел': 4, 'ма': 5, 'май': 5, 
            'июн': 6, 'июл': 7, 'август': 8, 'сентябр': 9, 
            'октябр': 10, 'ноябр': 11, 'декабр': 12
        }
        
        # Определяем месяц из имени файла
        month = None
        for month_name, month_num in months.items():
            if month_name.lower() in filename.lower():
                month = month_num
                break
        
        if not month:
            return None
        
        # Пытаемся найти диапазон дней в формате "1-15" или "16-30"
        import re
        day_range = re.search(r'(\d+)-(\d+)', filename)
        
        if day_range:
            # Берем последний день из диапазона
            last_day = int(day_range.group(2))
            
            # Определяем год (текущий)
            year = QDate.currentDate().year()
            
            # Создаем и возвращаем объект QDate
            return QDate(year, month, min(last_day, 28))  # страховка от некорректного дня
        
        return None
        
    def load_file(self, file_path):
        """Загружает файл"""
        self.current_file = file_path
        self.add_to_recent(file_path)
        self.status_card.show()
        self.status_label.setText(f"Файл загружен: {Path(file_path).name}")
        
        # Пытаемся извлечь дату из имени файла
        extracted_date = self.extract_date_from_filename(file_path)
        if extracted_date and extracted_date.isValid():
            self.invoice_date.setDate(extracted_date)
            self.show_notification(f"Дата определена из имени файла: {extracted_date.toString('dd MMMM yyyy')}", "info")
        else:
            # Если не удалось извлечь дату, используем текущую
            self.invoice_date.setDate(QDate.currentDate())
        
        # Активируем кнопки
        self.preview_btn.setEnabled(True)
        self.generate_btn.setEnabled(True)  # Активируем сразу кнопку создания документов
    
    def load_recent_file(self, item):
        """Загружает файл из истории"""
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if os.path.exists(file_path):
            self.load_file(file_path)
        else:
            self.recent_files.remove(file_path)
            self.update_recent_list()
            self.show_notification("Файл не найден", "error")
    
    def preview_data(self):
        """Предпросмотр данных"""
        try:
            # Если данные уже загружены и обработаны, используем их
            if not self.current_services:
                processor = DataProcessor()
                result = processor.process_file(self.current_file)
                
                if result.success:
                    self.current_services = result.data
                else:
                    self.show_notification(result.message, "error")
                    return
            
            # Показываем диалог с текущими данными
            self.show_preview_dialog(self.current_services)
            
        except Exception as e:
            self.show_notification(str(e), "error")
    
    def generate_documents(self):
        """Генерация документов"""
        try:
            # Проверяем, есть ли данные
            if not self.current_file:
                self.show_notification("Сначала выберите файл с данными", "warning")
                return
                
            # Если еще не обработали данные, делаем это сейчас
            if not self.current_services:
                processor = DataProcessor()
                result = processor.process_file(self.current_file)
                if not result.success:
                    self.show_notification(result.message, "error")
                    return
                self.current_services = result.data
            
            # Используем дату счета для имени файла
            invoice_date = self.invoice_date.date().toPyDate()
            default_filename = f"Счет_и_Акт_{invoice_date.strftime('%d_%m_%Y')}.xlsx"
            
            # Получаем путь для сохранения через диалог
            output_file, _ = QFileDialog.getSaveFileName(
                self,
                "Сохранить документы",
                str(Path("data/output") / default_filename),
                "Excel файлы (*.xlsx);;Все файлы (*.*)"
            )
            
            if not output_file:  # Пользователь отменил выбор
                return
                
            invoice_data = InvoiceData(
                number=self.invoice_number.text(),
                date=invoice_date,
                customer=self.config.get_customer_details().full_details,
                services=self.current_services
            )
            
            generator = DocumentGenerator(
                self.config.get_company_details(),
                self.config.get_customer_details()
            )
            
            if generator.generate_documents(invoice_data, output_file):
                self.print_btn.setEnabled(True)
                self.last_generated_file = output_file  # Сохраняем путь для печати
                self.show_notification("Документы успешно созданы!", "success")
            else:
                self.show_notification("Ошибка при создании документов", "error")
                
        except Exception as e:
            self.show_notification(str(e), "error")
    
    def print_documents(self):
        """Печать документов"""
        if not self.last_generated_file or not os.path.exists(self.last_generated_file):
            self.show_notification("Сначала создайте документы", "warning")
            return
            
        try:
            if sys.platform == 'win32':
                # Используем COM объекты на Windows для печати всех листов
                import win32com.client
                excel = win32com.client.Dispatch("Excel.Application")
                excel.Visible = False
                workbook = excel.Workbooks.Open(self.last_generated_file)
                try:
                    # Печатаем счет (первый лист)
                    workbook.Worksheets("Счет").PrintOut()
                    # Печатаем акт (второй лист)
                    workbook.Worksheets("Акт").PrintOut()
                    self.show_notification("Документы отправлены на печать", "success")
                finally:
                    # Закрываем без сохранения
                    workbook.Close(False)
                    excel.Quit()
            elif sys.platform == 'darwin':  # macOS
                # На macOS используем AppleScript для печати
                script = f'''
                tell application "Microsoft Excel"
                    open "{self.last_generated_file}"
                    tell active workbook
                        print worksheet "Счет" with properties {{copies:1}}
                        print worksheet "Акт" with properties {{copies:1}}
                        close saving no
                    end tell
                end tell
                '''
                subprocess.run(['osascript', '-e', script])
                self.show_notification("Документы отправлены на печать", "success")
            else:  # Linux
                # На Linux просто открываем файл
                self.show_notification("На Linux печать всех листов автоматически не поддерживается. Файл будет открыт.", "info")
                subprocess.run(['xdg-open', self.last_generated_file])
        except ImportError:
            # Если не удалось импортировать win32com, используем стандартный метод
            self.show_notification("Для печати всех листов установите pywin32 (pip install pywin32)", "warning")
            if sys.platform == 'win32':
                os.startfile(self.last_generated_file, 'print')
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', '-a', 'Microsoft Excel', self.last_generated_file])
            else:  # Linux
                subprocess.run(['xdg-open', self.last_generated_file])
        except Exception as e:
            self.show_notification(f"Ошибка печати: {str(e)}", "error")
            # Запасной вариант - просто открыть файл
            try:
                if sys.platform == 'win32':
                    os.startfile(self.last_generated_file)
                elif sys.platform == 'darwin':  # macOS
                    subprocess.run(['open', self.last_generated_file])
                else:  # Linux
                    subprocess.run(['xdg-open', self.last_generated_file])
            except:
                pass
    
    def open_settings(self):
        """Открытие настроек"""
        from paymentmaker.gui.modern_settings import ModernSettingsDialog
        dialog = ModernSettingsDialog(self.config, self)
        # Передаем текущую тему в диалог
        dialog.current_theme = self.current_theme
        dialog.theme = self.theme
        dialog.apply_theme()
        if dialog.exec():
            # Если настройки были сохранены, обновляем интерфейс
            self.show_notification("Настройки сохранены", "success")
    
    def show_notification(self, message, type="info"):
        """Показывает уведомление"""
        colors = {
            'info': self.theme['accent'],
            'success': self.theme['success'],
            'error': self.theme['error'],
            'warning': self.theme['warning']
        }
        
        notification = QLabel(message, self)
        notification.setStyleSheet(f"""
            background-color: {colors[type]};
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
        """)
        notification.setAlignment(Qt.AlignmentFlag.AlignCenter)
        notification.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        # Позиционирование
        notification.adjustSize()
        x = (self.width() - notification.width()) // 2
        y = self.height() - 100
        notification.move(x, y)
        notification.show()
        notification.raise_()
        
        # Автоскрытие через 3 секунды
        QTimer.singleShot(3000, notification.close)
    
    def add_to_recent(self, file_path):
        """Добавляет файл в историю"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:5]  # Максимум 5 файлов
        self.save_recent_files()
        self.update_recent_list()
    
    def update_recent_list(self):
        """Обновляет список недавних файлов"""
        self.recent_list.clear()
        for file_path in self.recent_files:
            if os.path.exists(file_path):
                item = QListWidgetItem(Path(file_path).name)
                item.setToolTip(file_path)
                item.setData(Qt.ItemDataRole.UserRole, file_path)
                self.recent_list.addItem(item)
    
    def load_recent_files(self):
        """Загружает историю файлов"""
        try:
            recent_files = self.config.get('paths.recent_files', [])
            if recent_files:
                self.recent_files = recent_files[:5]
        except:
            self.recent_files = []
        self.update_recent_list()
    
    def save_recent_files(self):
        """Сохраняет историю файлов"""
        self.config.set('paths.recent_files', self.recent_files)