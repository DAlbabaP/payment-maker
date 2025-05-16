"""
Модуль обработки данных из входных файлов
"""

import re
import logging
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Tuple
import pandas as pd

from paymentmaker.core.models import TransportService, ProcessingResult

logger = logging.getLogger(__name__)


class DataProcessor:
    """Класс для обработки входных данных"""
    
    # Словарь для исправления названий городов
    CITY_CORRECTIONS = {
        'о': 'Одинцово',
        'иево': 'Сергиев Посад',
        'иево-посадск': 'Сергиев Посад',
        'с. посад': 'Сергиев Посад',
        'с.посад': 'Сергиев Посад',
        'серг посад': 'Сергиев Посад',
        'серг. посад': 'Сергиев Посад',
        'сергиево': 'Сергиев Посад',
        'сергиев': 'Сергиев Посад',
        'киржачск': 'Киржач'
    }
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def process_file(self, file_path: str) -> ProcessingResult:
        """
        Обрабатывает входной файл с данными о перевозках
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            ProcessingResult с обработанными данными
        """
        self.errors = []
        self.warnings = []
        
        try:
            # Загружаем данные
            df = self._load_data(file_path)
            if df is None:
                return ProcessingResult(
                    success=False,
                    message="Не удалось загрузить файл",
                    errors=self.errors
                )
            
            # Проверяем структуру
            if not self._validate_structure(df):
                return ProcessingResult(
                    success=False,
                    message="Неверная структура файла",
                    errors=self.errors
                )
            
            # Обрабатываем данные
            services = self._process_data(df)
            
            return ProcessingResult(
                success=True,
                message=f"Обработано {len(services)} записей",
                data=services,
                warnings=self.warnings
            )
            
        except Exception as e:
            logger.exception(f"Ошибка при обработке файла: {e}")
            self.errors.append(str(e))
            return ProcessingResult(
                success=False,
                message=f"Критическая ошибка: {e}",
                errors=self.errors
            )
    
    def _load_data(self, file_path: str) -> Optional[pd.DataFrame]:
        """Загружает данные из файла"""
        try:
            # Пробуем загрузить как Excel
            df = pd.read_excel(file_path, engine='openpyxl')
            logger.info(f"Загружено {len(df)} строк из Excel файла")
            return df
        except Exception as e:
            logger.warning(f"Не удалось загрузить как Excel: {e}")
            
            # Пробуем загрузить как CSV
            encodings = ['utf-8', 'cp1251', 'latin1', 'ISO-8859-1']
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, sep='\t', encoding=encoding)
                    logger.info(f"Загружено {len(df)} строк из CSV с кодировкой {encoding}")
                    return df
                except Exception:
                    continue
            
            self.errors.append("Не удалось загрузить файл ни в одном из поддерживаемых форматов")
            return None
    
    def _validate_structure(self, df: pd.DataFrame) -> bool:
        """Проверяет структуру данных"""
        required_columns = ['Дата', 'Водитель', 'Авто', 'Адрес выгрузки', 'Сумма за рейсы']
        missing_columns = []
        
        # Проверяем наличие требуемых колонок
        for col in required_columns:
            if col not in df.columns:
                # Пробуем найти по частичному совпадению
                found = False
                for actual_col in df.columns:
                    if isinstance(actual_col, str) and col.lower() in actual_col.lower():
                        df.rename(columns={actual_col: col}, inplace=True)
                        found = True
                        break
                
                if not found:
                    missing_columns.append(col)
        
        if missing_columns:
            self.errors.append(f"Отсутствуют необходимые колонки: {', '.join(missing_columns)}")
            return False
        
        return True
    
    def _process_data(self, df: pd.DataFrame) -> List[TransportService]:
        """Обрабатывает данные и создает список услуг"""
        services = []
        
        for index, row in df.iterrows():
            try:
                service = self._process_row(row, index)
                if service:
                    services.append(service)
            except Exception as e:
                self.warnings.append(f"Ошибка в строке {index + 1}: {e}")
        
        return services
    
    def _process_row(self, row: pd.Series, index: int) -> Optional[TransportService]:
        """Обрабатывает одну строку данных"""
        # Извлекаем дату
        date = self._parse_date(row.get('Дата'), index)
        if not date:
            return None
        
        # Извлекаем информацию о водителе
        driver_name = self._extract_driver_name(row.get('Водитель'), index)
        
        # Извлекаем номер автомобиля
        car_number = self._extract_car_number(row.get('Авто'), index)
        
        # Определяем маршрут
        route = self._extract_route(row.get('Адрес выгрузки'), index)
        
        # Получаем сумму
        amount = self._parse_amount(row.get('Сумма за рейсы'), index)
        
        return TransportService(
            date=date,
            driver_name=driver_name,
            car_number=car_number,
            route=route,
            price=amount,
            amount=amount
        )
    
    def _parse_date(self, date_str: any, row_index: int) -> Optional[datetime]:
        """Парсит дату"""
        if pd.isna(date_str):
            self.warnings.append(f"Строка {row_index + 1}: пустая дата")
            return datetime.now()
        
        try:
            if isinstance(date_str, datetime):
                return date_str
            
            # Пробуем разные форматы
            for fmt in ['%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y']:
                try:
                    return datetime.strptime(str(date_str), fmt)
                except ValueError:
                    continue
            
            self.warnings.append(f"Строка {row_index + 1}: не удалось распознать дату '{date_str}'")
            return datetime.now()
            
        except Exception as e:
            self.warnings.append(f"Строка {row_index + 1}: ошибка при парсинге даты: {e}")
            return datetime.now()
    
    def _extract_driver_name(self, driver_info: any, row_index: int) -> str:
        """Извлекает имя водителя"""
        if pd.isna(driver_info):
            self.warnings.append(f"Строка {row_index + 1}: водитель не указан")
            return "НЕ УКАЗАН"
        
        driver_str = str(driver_info)
        if ',' in driver_str:
            return driver_str.split(',')[0].strip()
        
        self.warnings.append(f"Строка {row_index + 1}: не удалось извлечь имя водителя")
        return driver_str
    
    def _extract_car_number(self, car_info: any, row_index: int) -> str:
        """Извлекает номер автомобиля"""
        if pd.isna(car_info):
            self.warnings.append(f"Строка {row_index + 1}: автомобиль не указан")
            return "НЕ УКАЗАН"
        
        car_str = str(car_info)
        match = re.search(r'Газель\s+([А-Я0-9]+)', car_str)
        
        if match:
            return match.group(1)
        
        self.warnings.append(f"Строка {row_index + 1}: не удалось извлечь номер автомобиля")
        return "НЕ УКАЗАН"
    
    def _extract_route(self, address_text: any, row_index: int) -> List[str]:
        """Извлекает маршрут из адресов"""
        if pd.isna(address_text) or not address_text:
            self.warnings.append(f"Строка {row_index + 1}: адрес не указан")
            return ["Дмитров", "Неизвестный пункт"]
        
        # Используем существующую логику из старого кода
        locations = self._parse_addresses(str(address_text))
        
        if not locations:
            self.warnings.append(f"Строка {row_index + 1}: не удалось извлечь маршрут")
            return ["Дмитров", "Неизвестный пункт"]
        
        # Формируем маршрут
        route = ["Дмитров"]
        route.extend(locations[:3])  # Максимум 3 пункта назначения
        
        return route
    
    def _parse_addresses(self, address_text: str) -> List[str]:
        """Парсит адреса и извлекает города"""
        addresses = address_text.strip('"').split('\n')
        locations = {}
        
        for address in addresses:
            address = address.strip()
            if not address:
                continue
            
            # Проверяем известные сокращения
            for abbr, full_city in self.CITY_CORRECTIONS.items():
                if re.search(rf'\b{abbr}\b', address.lower()):
                    locations[full_city] = 3  # Высший приоритет
            
            # Ищем города в различных форматах
            patterns = [
                r'(?:го\s+|г\.\s*|город\s+|городской округ\s+)([А-Яа-я\-]+)',
                r'(?:^|\s)(Волоколамск|Одинцово|Сергиев\s*Посад|Киржач|Аленино)(?:\s|$|,)',
                r'([А-Яа-я\-]+)(?:\s+(?:муниципальный округ|район|го))',
                r'(?:с\.|д\.|п\.|село|деревня|поселок)\s*([А-Яа-я\-]+)'
            ]
            
            for i, pattern in enumerate(patterns):
                match = re.search(pattern, address, re.IGNORECASE)
                if match:
                    city = match.group(1).strip()
                    if city.lower() != "дмитров":
                        priority = 3 - i  # Убывающий приоритет
                        if city not in locations or locations[city] < priority:
                            locations[city] = priority
            
            # Извлекаем регион
            region_match = re.search(r'([А-Яа-я]+)\s+обл', address)
            region = region_match.group(1) if region_match else "Московская"
        
        # Сортируем по приоритету
        sorted_locs = sorted(
            [(loc, priority) for loc, priority in locations.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        return [loc for loc, _ in sorted_locs]
    
    def _parse_amount(self, amount_str: any, row_index: int) -> Decimal:
        """Парсит сумму"""
        if pd.isna(amount_str):
            self.warnings.append(f"Строка {row_index + 1}: сумма не указана")
            return Decimal("0.00")
        
        try:
            # Преобразуем в строку и очищаем
            amount_str = str(amount_str).replace(',', '.').replace(' ', '')
            return Decimal(amount_str)
        except Exception as e:
            self.warnings.append(f"Строка {row_index + 1}: не удалось преобразовать сумму: {e}")
            return Decimal("0.00")