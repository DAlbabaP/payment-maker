"""
Графический интерфейс PaymentMaker
"""

# Импортируем новые модули
from paymentmaker.gui.modern_ui import ModernMainWindow
from paymentmaker.gui.modern_settings import ModernSettingsDialog
from paymentmaker.gui.modern_widgets import ModernButton, FileDropZone
from paymentmaker.gui.modern_styles import ModernStyle

# Для обратной совместимости
PaymentMakerApp = ModernMainWindow
SettingsDialog = ModernSettingsDialog

__all__ = [
    'PaymentMakerApp',
    'ModernMainWindow',
    'SettingsDialog',
    'ModernSettingsDialog',
    'ModernButton',
    'FileDropZone',
    'ModernStyle'
]