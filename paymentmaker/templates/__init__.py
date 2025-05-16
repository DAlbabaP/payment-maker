"""
Модуль шаблонов документов
"""

from paymentmaker.templates.invoice import InvoiceTemplate
from paymentmaker.templates.act import ActTemplate
from paymentmaker.templates.styles import DocumentStyles

__all__ = [
    'InvoiceTemplate',
    'ActTemplate',
    'DocumentStyles'
]