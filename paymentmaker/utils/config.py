"""
Модуль конфигурации приложения
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from paymentmaker.core.models import CompanyDetails

logger = logging.getLogger(__name__)


class Config:
    """Класс для управления конфигурацией приложения"""
    
    CONFIG_FILE = "config.json"
    
    # Настройки по умолчанию
    DEFAULT_CONFIG = {
        "company": {
            "name": "ИП Демо",
            "inn": "000000000000",
            "address": "г. Москва, ул. Демонстрационная, д. 1",
            "phone": "т: 8-900-000-00-00",
            "bank_name": "ДЕМО БАНК",
            "bank_bik": "000000000",
            "bank_account": "00000000000000000000",
            "company_account": "00000000000000000000"
        },
        "customer": {
            "name": "ООО \"Компания\"",
            "inn": "0000000000",
            "address": "г. Москва, ул. Тестовая, д. 2",
            "phone": "",
            "bank_name": "ДЕМО БАНК КЛИЕНТА",
            "bank_bik": "000000000",
            "bank_account": "00000000000000000000",
            "company_account": "00000000000000000000"
        },
        # Остальная часть конфигурации остаётся без изменений
        "paths": {
            "last_input_dir": "",
            "last_output_dir": "",
            "last_input_file": ""
        },
        "interface": {
            "theme": "light",
            "window_size": [900, 700],
            "window_position": None
        }
    }
    
    def __init__(self):
        self.config_path = self._get_config_path()
        self.config = self._load_config()
    
    def _get_config_path(self) -> Path:
        """Получает путь к файлу конфигурации"""
        if hasattr(self, '_config_path'):
            return self._config_path
            
        # Определяем директорию для конфигурации
        if Path.home().name == 'root':
            config_dir = Path('/etc/paymentmaker')
        else:
            if Path.home().joinpath('.config').exists():
                config_dir = Path.home() / '.config' / 'paymentmaker'
            else:
                config_dir = Path.home() / '.paymentmaker'
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / self.CONFIG_FILE
    
    def _load_config(self) -> Dict[str, Any]:
        """Загружает конфигурацию из файла"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Объединяем с настройками по умолчанию (для новых полей)
                    return self._merge_configs(self.DEFAULT_CONFIG, config)
            except Exception as e:
                logger.error(f"Ошибка при загрузке конфигурации: {e}")
        
        # Возвращаем настройки по умолчанию
        self.save()  # Создаем файл с настройками по умолчанию
        return self.DEFAULT_CONFIG.copy()
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Объединяет загруженные настройки с настройками по умолчанию"""
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result:
                if isinstance(value, dict) and isinstance(result[key], dict):
                    result[key] = self._merge_configs(result[key], value)
                else:
                    result[key] = value
            else:
                result[key] = value
        
        return result
    
    def save(self) -> bool:
        """Сохраняет конфигурацию в файл"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info(f"Конфигурация сохранена: {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении конфигурации: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получает значение по ключу"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """Устанавливает значение по ключу"""
        keys = key.split('.')
        target = self.config
        
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        target[keys[-1]] = value
        return self.save()
    
    def get_company_details(self) -> CompanyDetails:
        """Возвращает реквизиты компании"""
        company_data = self.config.get('company', {})
        return CompanyDetails(
            name=company_data.get('name', ''),
            inn=company_data.get('inn', ''),
            address=company_data.get('address', ''),
            phone=company_data.get('phone', ''),
            bank_name=company_data.get('bank_name', ''),
            bank_bik=company_data.get('bank_bik', ''),
            bank_account=company_data.get('bank_account', ''),
            company_account=company_data.get('company_account', '')
        )
    
    def get_customer_details(self) -> CompanyDetails:
        """Возвращает реквизиты клиента по умолчанию"""
        customer_data = self.config.get('customer', {})
        return CompanyDetails(
            name=customer_data.get('name', ''),
            inn=customer_data.get('inn', ''),
            address=customer_data.get('address', ''),
            phone=customer_data.get('phone', ''),
            bank_name=customer_data.get('bank_name', ''),
            bank_bik=customer_data.get('bank_bik', ''),
            bank_account=customer_data.get('bank_account', ''),
            company_account=customer_data.get('company_account', '')
        )
    
    def update_company_details(self, details: CompanyDetails) -> bool:
        """Обновляет реквизиты компании"""
        self.config['company'] = {
            'name': details.name,
            'inn': details.inn,
            'address': details.address,
            'phone': details.phone,
            'bank_name': details.bank_name,
            'bank_bik': details.bank_bik,
            'bank_account': details.bank_account,
            'company_account': details.company_account
        }
        return self.save()
    
    def update_customer_details(self, details: CompanyDetails) -> bool:
        """Обновляет реквизиты клиента"""
        self.config['customer'] = {
            'name': details.name,
            'inn': details.inn,
            'address': details.address,
            'phone': details.phone,
            'bank_name': details.bank_name,
            'bank_bik': details.bank_bik,
            'bank_account': details.bank_account,
            'company_account': details.company_account
        }
        return self.save()
    
    def reset_to_defaults(self):
        """Сбрасывает конфигурацию к настройкам по умолчанию"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()