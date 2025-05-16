"""
Современный диалог настроек
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QScrollArea, QWidget,
    QTabWidget, QPushButton, QListWidget, QListWidgetItem,
    QComboBox, QInputDialog, QMessageBox, QMenu, QMenuBar,
    QFrame
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIcon, QAction

from paymentmaker.core.models import CompanyDetails
from paymentmaker.utils.config import Config
from paymentmaker.gui.modern_styles import ModernStyle
from paymentmaker.gui.modern_widgets import ModernButton


class ModernSettingsDialog(QDialog):
    """Современный диалог настроек"""
    
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.current_theme = 'light'  # По умолчанию
        self.theme = ModernStyle.get_theme()
        self.setWindowTitle("Настройки")
        self.setMinimumSize(700, 600)
        self.setModal(True)
        self._opacity_animation = None
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Создает интерфейс"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.theme['bg_primary']};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Заголовок
        self.header = self.create_header()
        layout.addWidget(self.header)
        
        # Табы
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(ModernStyle.get_tab_widget_style(self.theme))
        
        # Вкладка компании
        company_tab = self.create_company_tab()
        self.tabs.addTab(company_tab, "Реквизиты компании")
        
        # Вкладка заказчика
        customer_tab = self.create_customer_tab()
        self.tabs.addTab(customer_tab, "Реквизиты заказчика")
        
        # Вкладка шаблонов
        templates_tab = self.create_templates_tab()
        self.tabs.addTab(templates_tab, "Шаблоны реквизитов")
        
        layout.addWidget(self.tabs, 1)
        
        # Кнопки действий
        self.actions = self.create_actions()
        layout.addWidget(self.actions)
    
    def apply_theme(self):
        """Применяет тему к диалогу"""
        self.theme = ModernStyle.get_theme(self.current_theme)
        
        # Обновляем основной стиль
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.theme['bg_primary']};
            }}
        """)
        
        # Обновляем заголовок
        self.header.setStyleSheet(f"""
            background-color: {self.theme['bg_secondary']};
            border-bottom: 1px solid {self.theme['border']};
        """)
        
        # Обновляем метку в заголовке
        for label in self.header.findChildren(QLabel):
            label.setStyleSheet(f"""
                font-size: 24px;
                font-weight: 600;
                color: {self.theme['text_primary']};
            """)
        
        # Обновляем табы
        self.tabs.setStyleSheet(ModernStyle.get_tab_widget_style(self.theme))
        
        # Обновляем поля ввода
        for field_name, widget in self.company_fields.items():
            self.update_field_style(widget)
        
        for field_name, widget in self.customer_fields.items():
            self.update_field_style(widget)
        
        # Обновляем кнопки в действиях
        self.actions.setStyleSheet(f"""
            background-color: {self.theme['bg_secondary']};
            border-top: 1px solid {self.theme['border']};
        """)
        
        # Обновляем кнопки
        for button in self.findChildren(ModernButton):
            button.theme = self.theme
          # Обновляем метки в шаблонах
        for label in self.tabs.widget(2).findChildren(QLabel):
            if "font-size: 18px" in label.styleSheet():
                label.setStyleSheet(f"""
                    font-size: 18px;
                    font-weight: 600;
                    color: {self.theme['text_primary']};
                    margin-bottom: 16px;
                """)
            elif "font-size: 14px" in label.styleSheet():
                label.setStyleSheet(f"""
                    font-size: 14px;
                    color: {self.theme['text_secondary']};
                    margin-bottom: 32px;
                """)
        
        # Обновляем список шаблонов
        if hasattr(self, 'templates_list'):
            self.templates_list.setStyleSheet(ModernStyle.get_list_widget_style(self.theme))
        
        # Обновляем выпадающие списки
        if hasattr(self, 'template_type_combo'):
            self.template_type_combo.setStyleSheet(f"""
                QComboBox {{
                    background-color: {self.theme['bg_secondary']};
                    border: 2px solid {self.theme['border']};
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 14px;
                    color: {self.theme['text_primary']};
                    min-height: 48px;
                }}
                QComboBox:focus {{
                    border-color: {self.theme['accent']};
                }}
                QComboBox::drop-down {{
                    border: 0px;
                    width: 32px;
                }}
            """)
        
        # Обновляем стили для скролл областей
        for scroll in self.findChildren(QScrollArea):
            scroll.setStyleSheet(f"""
                QScrollArea {{
                    border: none;
                    background-color: {self.theme['bg_primary']};
                }}
                QScrollBar:vertical {{
                    background: {self.theme['bg_secondary']};
                    width: 8px;
                    border-radius: 4px;
                }}
                QScrollBar::handle:vertical {{
                    background: {self.theme['border']};
                    border-radius: 4px;
                    min-height: 20px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background: {self.theme['accent']};
                }}
            """)
            
            # Обновляем цвет фона для виджета внутри скролл области
            if scroll.widget():
                scroll.widget().setStyleSheet(f"background-color: {self.theme['bg_primary']};")
        
    
    def update_field_style(self, field_widget):
        """Обновляет стиль поля ввода"""
        # Обновляем метку
        label = field_widget.findChild(QLabel)
        if label:
            label.setStyleSheet(f"""
                font-size: 14px;
                font-weight: 500;
                color: {self.theme['text_secondary']};
            """)
        
        # Обновляем поле ввода
        line_edit = field_widget.line_edit
        if line_edit:
            line_edit.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {self.theme['bg_secondary']};
                    border: 2px solid {self.theme['border']};
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 14px;
                    color: {self.theme['text_primary']};
                }}
                QLineEdit:focus {{
                    border-color: {self.theme['accent']};
                }}
            """)
    
    def create_header(self):
        """Создает заголовок"""
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet(f"""
            background-color: {self.theme['bg_secondary']};
            border-bottom: 1px solid {self.theme['border']};
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(32, 0, 32, 0)
        
        title = QLabel("⚙️ Настройки")
        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 600;
            color: {self.theme['text_primary']};
        """)
        
        layout.addWidget(title)
        layout.addStretch()
        
        return header
    
    def create_company_tab(self):
        """Создает вкладку с реквизитами компании"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 32, 32, 32)
        
        # Добавляем выбор шаблона
        template_layout = QHBoxLayout()
        template_label = QLabel("Шаблон реквизитов:")
        template_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 500;
            color: {self.theme['text_secondary']};
        """)
        
        self.company_template_combo = QComboBox()
        self.company_template_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {self.theme['bg_secondary']};
                border: 2px solid {self.theme['border']};
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                color: {self.theme['text_primary']};
                min-height: 48px;
                max-width: 300px;
            }}
            QComboBox:focus {{
                border-color: {self.theme['accent']};
            }}
            QComboBox::drop-down {{
                border: 0px;
                width: 32px;
            }}
        """)
        self.company_template_combo.currentIndexChanged.connect(self.company_template_selected)
        template_layout.addWidget(template_label)
        template_layout.addWidget(self.company_template_combo)
        template_layout.addStretch()
        
        layout.addLayout(template_layout)
        
        # Создаем поля ввода
        self.company_fields = {}
        fields = [
            ("name", "Название организации"),
            ("inn", "ИНН"),
            ("address", "Адрес"),
            ("phone", "Телефон"),
            ("bank_name", "Банк"),
            ("bank_bik", "БИК"),
            ("bank_account", "Корр. счет"),
            ("company_account", "Расчетный счет")
        ]
        
        for field_name, label_text in fields:
            field_widget = self.create_field(label_text)
            self.company_fields[field_name] = field_widget
            layout.addWidget(field_widget)
        
        layout.addStretch()
        
        # Кнопка сохранения как шаблона
        save_as_template_btn = ModernButton("💾 Сохранить как шаблон")
        save_as_template_btn.clicked.connect(lambda: self.save_as_template("company"))
        layout.addWidget(save_as_template_btn)
        
        # Scrollable
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {self.theme['bg_primary']};
            }}
        """)
        
        return scroll
    
    def create_customer_tab(self):
        """Создает вкладку с реквизитами заказчика"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 32, 32, 32)
        
        # Добавляем выбор шаблона
        template_layout = QHBoxLayout()
        template_label = QLabel("Шаблон реквизитов:")
        template_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 500;
            color: {self.theme['text_secondary']};
        """)
        
        self.customer_template_combo = QComboBox()
        self.customer_template_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {self.theme['bg_secondary']};
                border: 2px solid {self.theme['border']};
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                color: {self.theme['text_primary']};
                min-height: 48px;
                max-width: 300px;
            }}
            QComboBox:focus {{
                border-color: {self.theme['accent']};
            }}
            QComboBox::drop-down {{
                border: 0px;
                width: 32px;
            }}
        """)
        self.customer_template_combo.currentIndexChanged.connect(self.customer_template_selected)
        template_layout.addWidget(template_label)
        template_layout.addWidget(self.customer_template_combo)
        template_layout.addStretch()
        
        layout.addLayout(template_layout)
        
        # Создаем поля ввода
        self.customer_fields = {}
        fields = [
            ("name", "Название организации"),
            ("inn", "ИНН"),
            ("address", "Адрес"),
            ("phone", "Телефон"),
            ("bank_name", "Банк"),
            ("bank_bik", "БИК"),
            ("bank_account", "Корр. счет"),
            ("company_account", "Расчетный счет")
        ]
        
        for field_name, label_text in fields:
            field_widget = self.create_field(label_text)
            self.customer_fields[field_name] = field_widget
            layout.addWidget(field_widget)
        
        layout.addStretch()
        
        # Кнопка сохранения как шаблона
        save_as_template_btn = ModernButton("💾 Сохранить как шаблон")
        save_as_template_btn.clicked.connect(lambda: self.save_as_template("customer"))
        layout.addWidget(save_as_template_btn)
        
        # Scrollable
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {self.theme['bg_primary']};
            }}
        """)
        
        return scroll
    
    def create_templates_tab(self):
        """Создает вкладку с шаблонами реквизитов"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 32, 32, 32)
        
        # Заголовок
        title = QLabel("Управление шаблонами реквизитов")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 600;
            color: {self.theme['text_primary']};
            margin-bottom: 16px;
        """)
        layout.addWidget(title)
        
        # Описание
        desc = QLabel("Здесь вы можете создавать, редактировать и удалять шаблоны реквизитов для компаний и заказчиков")
        desc.setStyleSheet(f"""
            font-size: 14px;
            color: {self.theme['text_secondary']};
            margin-bottom: 32px;
        """)
        layout.addWidget(desc)
        
        # Тип шаблона
        type_layout = QHBoxLayout()
        type_label = QLabel("Тип шаблона:")
        type_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 500;
            color: {self.theme['text_secondary']};
        """)
        
        self.template_type_combo = QComboBox()
        self.template_type_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {self.theme['bg_secondary']};
                border: 2px solid {self.theme['border']};
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                color: {self.theme['text_primary']};
                min-height: 48px;
                max-width: 250px;
            }}
            QComboBox:focus {{
                border-color: {self.theme['accent']};
            }}
            QComboBox::drop-down {{
                border: 0px;
                width: 32px;
            }}
        """)
        self.template_type_combo.addItem("Компания", "company")
        self.template_type_combo.addItem("Заказчик", "customer")
        self.template_type_combo.currentIndexChanged.connect(self.update_templates_list)
        
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.template_type_combo)
        type_layout.addStretch()
        
        layout.addLayout(type_layout)
        
        # Список шаблонов
        list_label = QLabel("Доступные шаблоны:")
        list_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 500;
            color: {self.theme['text_secondary']};
            margin-top: 16px;
        """)
        layout.addWidget(list_label)
        
        self.templates_list = QListWidget()
        self.templates_list.setStyleSheet(ModernStyle.get_list_widget_style(self.theme))
        self.templates_list.setMinimumHeight(200)
        layout.addWidget(self.templates_list)
        
        # Кнопки действий для шаблонов
        templates_buttons = QHBoxLayout()
        
        self.create_template_btn = ModernButton("➕ Создать")
        self.create_template_btn.clicked.connect(self.create_new_template)
        
        self.edit_template_btn = ModernButton("✏️ Редактировать")
        self.edit_template_btn.clicked.connect(self.edit_selected_template)
        
        self.delete_template_btn = ModernButton("🗑️ Удалить")
        self.delete_template_btn.clicked.connect(self.delete_selected_template)
        
        templates_buttons.addWidget(self.create_template_btn)
        templates_buttons.addWidget(self.edit_template_btn)
        templates_buttons.addWidget(self.delete_template_btn)
        templates_buttons.addStretch()
        
        layout.addLayout(templates_buttons)
        layout.addStretch()
        
        # Обновляем список шаблонов
        self.update_templates_list()
        
        return widget
    
    def create_field(self, label_text):
        """Создает поле ввода с меткой"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 16)
        
        label = QLabel(label_text)
        label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 500;
            color: {self.theme['text_secondary']};
        """)
        
        edit = QLineEdit()
        edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.theme['bg_secondary']};
                border: 2px solid {self.theme['border']};
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                color: {self.theme['text_primary']};
            }}
            QLineEdit:focus {{
                border-color: {self.theme['accent']};
            }}
        """)
        
        layout.addWidget(label)
        layout.addWidget(edit)
        
        widget.line_edit = edit
        return widget
    
    def create_actions(self):
        """Создает кнопки действий"""
        widget = QWidget()
        widget.setStyleSheet(f"""
            background-color: {self.theme['bg_secondary']};
            border-top: 1px solid {self.theme['border']};
        """)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(32, 16, 32, 16)
        
        layout.addStretch()
        
        self.cancel_btn = ModernButton("Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = ModernButton("Сохранить", primary=True)
        self.save_btn.clicked.connect(self.save_settings)
        
        layout.addWidget(self.cancel_btn)
        layout.addWidget(self.save_btn)
        
        return widget
    
    def load_data(self):
        """Загружает данные из конфигурации"""
        # Загружаем данные компании
        company = self.config.get_company_details()
        for field_name, widget in self.company_fields.items():
            value = getattr(company, field_name, "")
            widget.line_edit.setText(value)
        
        # Загружаем данные заказчика
        customer = self.config.get_customer_details()
        for field_name, widget in self.customer_fields.items():
            value = getattr(customer, field_name, "")
            widget.line_edit.setText(value)
            
        # Загружаем шаблоны в выпадающие списки
        self.load_templates_to_combos()
    
    def load_templates_to_combos(self):
        """Загружает шаблоны в выпадающие списки"""
        # Очищаем комбобоксы
        self.company_template_combo.clear()
        self.customer_template_combo.clear()
        
        # Добавляем стандартный элемент "Выберите шаблон"
        self.company_template_combo.addItem("Выберите шаблон...")
        self.customer_template_combo.addItem("Выберите шаблон...")
        
        # Получаем шаблоны из конфигурации
        company_templates = self.config.get('templates.company', [])
        customer_templates = self.config.get('templates.customer', [])
        
        # Заполняем комбобокс компании
        for template in company_templates:
            name = template.get('name', '')
            if name:
                self.company_template_combo.addItem(name, template)
        
        # Заполняем комбобокс заказчика
        for template in customer_templates:
            name = template.get('name', '')
            if name:
                self.customer_template_combo.addItem(name, template)
    
    def company_template_selected(self, index):
        """Обрабатывает выбор шаблона компании"""
        if index == 0:  # "Выберите шаблон..."
            return
        
        template = self.company_template_combo.currentData()
        if not template:
            return
        
        # Заполняем поля значениями из шаблона
        for field_name, widget in self.company_fields.items():
            value = template.get(field_name, '')
            widget.line_edit.setText(value)
    
    def customer_template_selected(self, index):
        """Обрабатывает выбор шаблона заказчика"""
        if index == 0:  # "Выберите шаблон..."
            return
        
        template = self.customer_template_combo.currentData()
        if not template:
            return
        
        # Заполняем поля значениями из шаблона
        for field_name, widget in self.customer_fields.items():
            value = template.get(field_name, '')
            widget.line_edit.setText(value)
    
    def save_as_template(self, template_type):
        """Сохраняет текущие реквизиты как шаблон"""
        # Определяем, какие поля использовать
        fields = self.company_fields if template_type == "company" else self.customer_fields
        
        # Запрашиваем имя шаблона
        name, ok = QInputDialog.getText(
            self, 
            f"Сохранение шаблона {template_type}", 
            "Введите имя для шаблона:",
            text=""
        )
        
        if not ok or not name:
            return
        
        # Собираем данные из полей
        template_data = {'name': name}
        for field_name, widget in fields.items():
            template_data[field_name] = widget.line_edit.text()
        
        # Получаем существующие шаблоны
        templates_key = f"templates.{template_type}"
        templates = self.config.get(templates_key, [])
        
        # Проверяем, существует ли шаблон с таким именем
        for i, template in enumerate(templates):
            if template.get('name') == name:
                # Спрашиваем о перезаписи
                msgbox = QMessageBox()
                msgbox.setIcon(QMessageBox.Icon.Question)
                msgbox.setText(f"Шаблон с именем '{name}' уже существует.")
                msgbox.setInformativeText("Хотите перезаписать его?")
                msgbox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                msgbox.setDefaultButton(QMessageBox.StandardButton.No)
                
                if msgbox.exec() == QMessageBox.StandardButton.Yes:
                    # Перезаписываем
                    templates[i] = template_data
                    self.config.set(templates_key, templates)
                    self.update_templates_list()
                    self.load_templates_to_combos()
                    return
                else:
                    # Отменяем
                    return
        
        # Добавляем новый шаблон
        templates.append(template_data)
        self.config.set(templates_key, templates)
        
        # Обновляем списки
        self.update_templates_list()
        self.load_templates_to_combos()
        
        # Показываем уведомление
        QMessageBox.information(self, "Шаблон сохранен", f"Шаблон '{name}' успешно сохранен.")
    
    def update_templates_list(self):
        """Обновляет список шаблонов на вкладке шаблонов"""
        self.templates_list.clear()
        
        # Определяем тип шаблона
        template_type = self.template_type_combo.currentData()
        if not template_type:
            return
        
        # Получаем шаблоны из конфигурации
        templates_key = f"templates.{template_type}"
        templates = self.config.get(templates_key, [])
        
        # Заполняем список
        for template in templates:
            name = template.get('name', '')
            if name:
                item = QListWidgetItem(name)
                item.setData(Qt.ItemDataRole.UserRole, template)
                self.templates_list.addItem(item)
    
    def create_new_template(self):
        """Создает новый шаблон"""
        # Определяем тип шаблона
        template_type = self.template_type_combo.currentData()
        if not template_type:
            return
        
        # Запрашиваем имя шаблона
        name, ok = QInputDialog.getText(
            self, 
            f"Создание шаблона {template_type}", 
            "Введите имя для нового шаблона:",
            text=""
        )
        
        if not ok or not name:
            return
        
        # Создаем пустой шаблон
        template_data = {'name': name}
        
        # Получаем существующие шаблоны
        templates_key = f"templates.{template_type}"
        templates = self.config.get(templates_key, [])
        
        # Проверяем, существует ли шаблон с таким именем
        for template in templates:
            if template.get('name') == name:
                QMessageBox.warning(self, "Ошибка", f"Шаблон с именем '{name}' уже существует.")
                return
        
        # Добавляем новый шаблон
        templates.append(template_data)
        self.config.set(templates_key, templates)
        
        # Обновляем списки
        self.update_templates_list()
        self.load_templates_to_combos()
        
        # Выбираем созданный шаблон для редактирования
        self.edit_template(template_data, template_type)
    
    def edit_selected_template(self):
        """Редактирует выбранный шаблон"""
        # Проверяем, выбран ли шаблон
        current_item = self.templates_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ошибка", "Не выбран шаблон для редактирования.")
            return
        
        # Получаем данные шаблона
        template = current_item.data(Qt.ItemDataRole.UserRole)
        if not template:
            return
        
        # Определяем тип шаблона
        template_type = self.template_type_combo.currentData()
        if not template_type:
            return
        
        # Открываем диалог редактирования
        self.edit_template(template, template_type)
    
    def edit_template(self, template, template_type):
        """Открывает диалог редактирования шаблона"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Редактирование шаблона: {template.get('name', '')}")
        dialog.setMinimumSize(600, 500)
        dialog.setModal(True)
        
        # Создаем макет
        layout = QVBoxLayout(dialog)
        
        # Создаем поля ввода
        fields_widget = QWidget()
        fields_layout = QVBoxLayout(fields_widget)
        
        # Поле для имени шаблона
        name_field = self.create_field("Название шаблона")
        name_field.line_edit.setText(template.get('name', ''))
        fields_layout.addWidget(name_field)
        
        # Поля для реквизитов
        field_widgets = {}
        fields = [
            ("name", "Название организации"),
            ("inn", "ИНН"),
            ("address", "Адрес"),
            ("phone", "Телефон"),
            ("bank_name", "Банк"),
            ("bank_bik", "БИК"),
            ("bank_account", "Корр. счет"),
            ("company_account", "Расчетный счет")
        ]
        
        for field_name, label_text in fields:
            field_widget = self.create_field(label_text)
            field_widget.line_edit.setText(template.get(field_name, ''))
            field_widgets[field_name] = field_widget
            fields_layout.addWidget(field_widget)
        
        fields_layout.addStretch()
        
        # Создаем scrollable для полей
        scroll = QScrollArea()
        scroll.setWidget(fields_widget)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {self.theme['bg_primary']};
            }}
        """)
        
        layout.addWidget(scroll, 1)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        cancel_btn = ModernButton("Отмена")
        cancel_btn.clicked.connect(dialog.reject)
        
        save_btn = ModernButton("Сохранить", primary=True)
        save_btn.clicked.connect(dialog.accept)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
        
        # Показываем диалог
        if dialog.exec():
            # Обновляем данные шаблона
            template['name'] = name_field.line_edit.text()
            
            for field_name, widget in field_widgets.items():
                template[field_name] = widget.line_edit.text()
            
            # Сохраняем в конфигурацию
            templates_key = f"templates.{template_type}"
            templates = self.config.get(templates_key, [])
            
            # Находим и обновляем шаблон
            found = False
            for i, t in enumerate(templates):
                if t.get('name') == template.get('name'):
                    templates[i] = template
                    found = True
                    break
            
            if not found:
                templates.append(template)
            
            self.config.set(templates_key, templates)
            
            # Обновляем списки
            self.update_templates_list()
            self.load_templates_to_combos()
    
    def delete_selected_template(self):
        """Удаляет выбранный шаблон"""
        # Проверяем, выбран ли шаблон
        current_item = self.templates_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ошибка", "Не выбран шаблон для удаления.")
            return
        
        # Получаем данные шаблона
        template = current_item.data(Qt.ItemDataRole.UserRole)
        if not template:
            return
        
        # Определяем тип шаблона
        template_type = self.template_type_combo.currentData()
        if not template_type:
            return
        
        # Подтверждение удаления
        msgbox = QMessageBox()
        msgbox.setIcon(QMessageBox.Icon.Question)
        msgbox.setText(f"Вы действительно хотите удалить шаблон '{template.get('name', '')}'?")
        msgbox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msgbox.setDefaultButton(QMessageBox.StandardButton.No)
        
        if msgbox.exec() != QMessageBox.StandardButton.Yes:
            return
        
        # Получаем существующие шаблоны
        templates_key = f"templates.{template_type}"
        templates = self.config.get(templates_key, [])
        
        # Удаляем шаблон
        templates = [t for t in templates if t.get('name') != template.get('name')]
        self.config.set(templates_key, templates)
        
        # Обновляем списки
        self.update_templates_list()
        self.load_templates_to_combos()
        
        # Показываем уведомление
        QMessageBox.information(self, "Шаблон удален", f"Шаблон '{template.get('name', '')}' был успешно удален.")
    
    def save_settings(self):
        """Сохраняет настройки"""
        # Сохраняем данные компании
        company_data = {}
        for field_name, widget in self.company_fields.items():
            company_data[field_name] = widget.line_edit.text()
        
        company = CompanyDetails(**company_data)
        self.config.update_company_details(company)
        
        # Сохраняем данные заказчика
        customer_data = {}
        for field_name, widget in self.customer_fields.items():
            customer_data[field_name] = widget.line_edit.text()
        
        customer = CompanyDetails(**customer_data)
        self.config.update_customer_details(customer)
        
        self.accept()