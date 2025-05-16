"""
Стили для документов Excel
"""

from openpyxl.styles import Font, Alignment, Border, Side, PatternFill


class DocumentStyles:
    """Стили для оформления документов"""
    
    @staticmethod
    def get_header_font():
        """Шрифт для заголовков"""
        return Font(name='Arial', size=10, bold=True)
    
    @staticmethod
    def get_normal_font():
        """Обычный шрифт"""
        return Font(name='Arial', size=10)
    
    @staticmethod
    def get_small_font():
        """Мелкий шрифт"""
        return Font(name='Arial', size=8)
    
    @staticmethod
    def get_title_font():
        """Шрифт для заголовка документа"""
        return Font(name='Arial', size=12, bold=True)
    
    @staticmethod
    def get_thin_border():
        """Тонкая граница"""
        side = Side(style='thin')
        return Border(left=side, right=side, top=side, bottom=side)
    
    @staticmethod
    def get_thick_border():
        """Толстая нижняя граница"""
        thin = Side(style='thin')
        thick = Side(style='thick')
        return Border(left=thin, right=thin, top=thin, bottom=thick)
    
    @staticmethod
    def get_header_fill():
        """Заливка для заголовков"""
        return PatternFill(start_color="E0E0E0", end_color="E0E0E0", fill_type="solid")
    
    @staticmethod
    def get_center_alignment():
        """Выравнивание по центру"""
        return Alignment(horizontal='center', vertical='center')
    
    @staticmethod
    def get_right_alignment():
        """Выравнивание справа"""
        return Alignment(horizontal='right', vertical='center')
    
    @staticmethod
    def get_left_alignment():
        """Выравнивание слева"""
        return Alignment(horizontal='left', vertical='center')
    
    @staticmethod
    def get_wrap_text_alignment():
        """Выравнивание с переносом текста"""
        return Alignment(wrap_text=True, vertical='center')