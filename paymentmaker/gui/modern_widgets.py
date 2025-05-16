"""
Кастомные виджеты для современного интерфейса
"""

from PyQt6.QtWidgets import (
    QPushButton, QFrame, QVBoxLayout, QLabel, QFileDialog,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty
)
from PyQt6.QtGui import (
    QColor, QDragEnterEvent, QDropEvent
)

from paymentmaker.gui.modern_styles import ModernStyle


class ModernButton(QPushButton):
    """Современная кнопка с анимацией"""
    
    def __init__(self, text, primary=False, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self._theme = ModernStyle.get_theme()
        self._shadow_animation = None
        self.setup_style()
        self.setup_animation()
    
    @property
    def theme(self):
        return self._theme
    
    @theme.setter
    def theme(self, value):
        self._theme = value
        self.setup_style()
    
    def setup_style(self):
        self.setMinimumHeight(48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(ModernStyle.get_button_style(self._theme, self.primary))
    
    def setup_animation(self):
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setOffset(0, 2)
        self.shadow.setBlurRadius(8)
        self.shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(self.shadow)
    
    def enterEvent(self, event):
        self.animate_shadow(20)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.animate_shadow(8)
        super().leaveEvent(event)
    
    def animate_shadow(self, blur_radius):
        if self._shadow_animation:
            self._shadow_animation.stop()
        
        self._shadow_animation = QPropertyAnimation(self.shadow, b"blurRadius")
        self._shadow_animation.setDuration(200)
        self._shadow_animation.setEndValue(blur_radius)
        self._shadow_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._shadow_animation.start()


class FileDropZone(QFrame):
    """Зона для перетаскивания файлов"""
    
    fileDropped = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('FileDropZone')  # Важно для идентификации
        self.setAcceptDrops(True)
        self._theme = ModernStyle.get_theme()
        self._icon_label = None
        self._text_label = None
        self.setup_ui()
    
    @property
    def theme(self):
        return self._theme
    
    @theme.setter
    def theme(self, value):
        self._theme = value
        self.update_style()
        # Обновляем стиль текстовой метки
        if self._text_label:
            self._text_label.setStyleSheet(f"""
                color: {self._theme['text_secondary']};
                font-size: 16px;
            """)
    
    def setup_ui(self):
        self.setMinimumHeight(120)
        self.update_style()
        
        # Создаем макет если его нет
        if self.layout() is None:
            layout = QVBoxLayout(self)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.setContentsMargins(16, 16, 16, 16)
        else:
            layout = self.layout()
        
        # Создаем или обновляем метки
        if self._icon_label is None:
            self._icon_label = QLabel("📁")
            self._icon_label.setStyleSheet("font-size: 48px;")
            self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self._icon_label)
        
        if self._text_label is None:
            self._text_label = QLabel("Перетащите файл сюда или нажмите для выбора")
            self._text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self._text_label)
        
        # Обновляем стиль текстовой метки
        self._text_label.setStyleSheet(f"""
            color: {self._theme['text_secondary']};
            font-size: 16px;
        """)
    
    def update_style(self):
        """Обновляет стиль виджета"""
        self.setStyleSheet(f"""
            QFrame#FileDropZone {{
                background-color: {self._theme['bg_secondary']};
                border: 2px dashed {self._theme['border']};
                border-radius: 12px;
            }}
            QFrame#FileDropZone:hover {{
                border-color: {self._theme['accent']};
                background-color: {self._theme['bg_accent']};
            }}
        """)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(f"""
                QFrame#FileDropZone {{
                    background-color: {self._theme['bg_accent']};
                    border: 2px solid {self._theme['accent']};
                    border-radius: 12px;
                }}
            """)
    
    def dragLeaveEvent(self, event):
        self.update_style()
    
    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.fileDropped.emit(files[0])
        self.dragLeaveEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Выберите файл",
                "",
                "Excel файлы (*.xlsx *.xls);;Все файлы (*.*)"
            )
            if file_path:
                self.fileDropped.emit(file_path)