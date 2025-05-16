"""
Модели данных для PaymentMaker
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from decimal import Decimal


@dataclass
class TransportService:
    """Модель транспортной услуги"""
    date: datetime
    driver_name: str
    car_number: str
    route: List[str]
    quantity: int = 1
    unit: str = "шт."
    price: Decimal = Decimal("0.00")
    amount: Decimal = Decimal("0.00")
    
    @property
    def description(self) -> str:
        """Формирует описание услуги"""
        date_str = self.date.strftime("%d.%m.%Y")
        route_str = " - ".join(self.route)
        return (f"Транспортные услуги {date_str} водит. {self.driver_name}, "
                f"а/м Газель {self.car_number}, маршрут {route_str}")


@dataclass
class InvoiceData:
    """Модель данных для счета"""
    number: str
    date: datetime
    customer: str
    customer_details: Optional[str] = None
    services: List[TransportService] = field(default_factory=list)
    
    @property
    def total_amount(self) -> Decimal:
        """Вычисляет общую сумму"""
        return sum(service.amount for service in self.services)
    
    @property
    def services_count(self) -> int:
        """Количество услуг"""
        return len(self.services)
    
    @property
    def date_str(self) -> str:
        """Форматированная дата"""
        months = {
            1: "января", 2: "февраля", 3: "марта", 4: "апреля",
            5: "мая", 6: "июня", 7: "июля", 8: "августа",
            9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
        }
        return f"{self.date.day} {months[self.date.month]} {self.date.year}"


@dataclass
class ActData(InvoiceData):
    """Модель данных для акта (наследует от счета)"""
    pass


@dataclass
class CompanyDetails:
    """Реквизиты компании"""
    name: str
    inn: str
    address: str
    phone: str
    bank_name: str
    bank_bik: str
    bank_account: str
    company_account: str
    
    @property
    def full_details(self) -> str:
        """Полные реквизиты"""
        return (f"{self.name}, ИНН {self.inn}, {self.address} {self.phone}")
    
    @property
    def bank_details(self) -> str:
        """Банковские реквизиты"""
        return (f"р/с {self.company_account}, в банке {self.bank_name}, "
                f"БИК {self.bank_bik}, к/с {self.bank_account}")


@dataclass
class ProcessingResult:
    """Результат обработки данных"""
    success: bool
    message: str
    data: Optional[List[TransportService]] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)