"""
Современные стили для PaymentMaker - отдельный модуль
"""

from PyQt6.QtGui import QColor


class ModernStyle:
    """Современные стили и темы"""
    
    # Цветовые схемы
    THEMES = {
        'light': {
            'bg_primary': '#FFFFFF',
            'bg_secondary': '#F5F5F5',
            'bg_accent': '#E3F2FD',
            'text_primary': '#212121',
            'text_secondary': '#757575',
            'accent': '#2196F3',
            'accent_hover': '#1976D2',
            'success': '#4CAF50',
            'error': '#F44336',
            'warning': '#FF9800',
            'border': '#E0E0E0',
            'shadow': 'rgba(0, 0, 0, 0.1)'
        },
        'dark': {
            'bg_primary': '#121212',
            'bg_secondary': '#1E1E1E',
            'bg_accent': '#1F2937',
            'text_primary': '#FFFFFF',
            'text_secondary': '#BDBDBD',
            'accent': '#2196F3',
            'accent_hover': '#1976D2',
            'success': '#4CAF50',
            'error': '#F44336',
            'warning': '#FF9800',
            'border': '#424242',
            'shadow': 'rgba(0, 0, 0, 0.3)'
        }
    }
    
    @staticmethod
    def get_theme(theme_name='light'):
        return ModernStyle.THEMES.get(theme_name, ModernStyle.THEMES['light'])
    
    @staticmethod
    def get_button_style(theme, primary=False):
        """Возвращает стиль для кнопки"""
        if primary:
            return f"""
                QPushButton {{
                    background-color: {theme['accent']};
                    color: white;
                    border: none;
                    border-radius: 24px;
                    font-size: 16px;
                    font-weight: 500;
                    padding: 0 32px;
                    min-height: 48px;
                }}
                QPushButton:hover {{
                    background-color: {theme['accent_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {theme['accent']};
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {theme['accent']};
                    border: 2px solid {theme['accent']};
                    border-radius: 24px;
                    font-size: 16px;
                    font-weight: 500;
                    padding: 0 32px;
                    min-height: 48px;
                }}
                QPushButton:hover {{
                    background-color: {theme['bg_accent']};
                }}
                QPushButton:pressed {{
                    background-color: {theme['bg_secondary']};
                }}
            """
    
    @staticmethod
    def get_input_style(theme):
        """Возвращает стиль для поля ввода"""
        return f"""
            QLineEdit {{
                background-color: {theme['bg_secondary']};
                border: 2px solid {theme['border']};
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                color: {theme['text_primary']};
            }}
            QLineEdit:focus {{
                border-color: {theme['accent']};
            }}
        """
    
    @staticmethod
    def get_card_style(theme):
        """Возвращает стиль для карточки"""
        return f"""
            QFrame {{
                background-color: {theme['bg_secondary']};
                border-radius: 12px;
                border: 1px solid {theme['border']};
            }}
        """
    @staticmethod
    def get_table_style(theme):
        """Возвращает стиль для таблицы"""
        return f"""
            QTableView {{
                background-color: {theme['bg_secondary']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                gridline-color: {theme['border']};
                color: {theme['text_primary']};
            }}
            QTableView::item {{
                padding: 8px;
            }}
            QTableView::item:selected {{
                background-color: {theme['accent']};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {theme['bg_secondary']};
                color: {theme['text_primary']};
                padding: 12px;
                border: none;
                font-weight: 600;
            }}
        """
    
    @staticmethod
    def get_tab_widget_style(theme):
        """Возвращает стиль для вкладок"""
        return f"""
            QTabWidget::pane {{
                background-color: {theme['bg_primary']};
                border: none;
            }}
            QTabBar::tab {{
                background-color: {theme['bg_secondary']};
                color: {theme['text_secondary']};
                padding: 12px 24px;
                margin: 0 4px;
                border: none;
                border-radius: 8px 8px 0 0;
            }}
            QTabBar::tab:selected {{
                background-color: {theme['bg_primary']};
                color: {theme['text_primary']};
                font-weight: 600;
            }}
            QTabBar::tab:hover {{
                background-color: {theme['bg_accent']};
            }}
        """
    @staticmethod
    def get_list_widget_style(theme):
        """Возвращает стиль для списка"""
        return f"""
            QListWidget {{
                background-color: {theme['bg_secondary']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                padding: 8px;
                color: {theme['text_primary']};
            }}
            QListWidget::item {{
                padding: 8px;
                margin: 2px 0;
                border-radius: 4px;
                color: {theme['text_primary']};
            }}
            QListWidget::item:hover {{
                background-color: {theme['bg_accent']};
            }}
            QListWidget::item:selected {{
                background-color: {theme['accent']};
                color: white;
            }}
        """
    
    @staticmethod
    def get_date_edit_style(theme):
        """Возвращает стиль для выбора даты"""
        return f"""
            QDateEdit {{
                background-color: {theme['bg_secondary']};
                border: 2px solid {theme['border']};
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                color: {theme['text_primary']};
            }}
            QDateEdit:focus {{
                border-color: {theme['accent']};
            }}
            QDateEdit::drop-down {{
                border: 0px;
                width: 32px;
            }}
        """
    
    @staticmethod
    def get_scroll_area_style(theme):
        """Возвращает стиль для области прокрутки"""
        return f"""
            QScrollArea {{
                border: none;
                background-color: {theme['bg_primary']};
            }}
            QScrollBar:vertical {{
                background: {theme['bg_secondary']};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {theme['border']};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {theme['accent']};
            }}
        """