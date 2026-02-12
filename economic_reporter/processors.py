from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from .reader import CSVReader


class ReportProcessor(ABC):
    """Абстрактный базовый класс для обработчиков отчетов"""

    def __init__(self):
        self.reader = CSVReader(self.required_columns)

    @property
    @abstractmethod
    def required_columns(self) -> List[str]:
        """Возвращает список необходимых колонок для отчета"""
        pass

    @abstractmethod
    def process(self, data: List[Dict[str, Any]]) -> List[Tuple[str, float]]:
        """
        Обрабатывает данные и возвращает результат

        Args:
            data: список словарей с данными

        Returns:
            Список кортежей (ключ, значение) для отчета
        """
        pass

    def execute(self, file_paths: List[str]) -> List[Tuple[str, float]]:
        """Полный цикл выполнения: чтение и обработка"""
        data = self.reader.read_files(file_paths)
        return self.process(data)


class AverageGDPProcessor(ReportProcessor):
    """Процессор для расчета среднего ВВП по странам"""

    @property
    def required_columns(self) -> List[str]:
        return ['country', 'gdp']

    def process(self, data: List[Dict[str, Any]]) -> List[Tuple[str, float]]:
        # Группируем данные по странам
        grouped_data = self.reader.group_by_column(data, 'country')

        results = []
        for country, records in grouped_data.items():
            gdp_values = []
            for record in records:
                try:
                    # Преобразуем значение gdp в float
                    gdp_str = str(record['gdp']).replace(',', '').strip()
                    gdp_value = float(gdp_str)
                    gdp_values.append(gdp_value)
                except (ValueError, KeyError):
                    continue  # Пропускаем некорректные записи

            if gdp_values:
                avg_gdp = sum(gdp_values) / len(gdp_values)
                results.append((country, round(avg_gdp, 2)))

        return results


class AverageUnemploymentProcessor(ReportProcessor):
    """Процессор для расчета средней безработицы по странам"""

    @property
    def required_columns(self) -> List[str]:
        return ['country', 'unemployment']

    def process(self, data: List[Dict[str, Any]]) -> List[Tuple[str, float]]:
        grouped_data = self.reader.group_by_column(data, 'country')

        results = []
        for country, records in grouped_data.items():
            unemployment_values = []
            for record in records:
                try:
                    unemployment_str = str(record['unemployment']).strip()
                    unemployment_value = float(unemployment_str)
                    unemployment_values.append(unemployment_value)
                except (ValueError, KeyError):
                    continue

            if unemployment_values:
                avg_unemployment = sum(unemployment_values) / len(unemployment_values)
                results.append((country, round(avg_unemployment, 2)))

        return results


class PopulationByContinentProcessor(ReportProcessor):
    """Процессор для расчета населения по континентам"""

    @property
    def required_columns(self) -> List[str]:
        return ['continent', 'population']

    def process(self, data: List[Dict[str, Any]]) -> List[Tuple[str, float]]:
        grouped_data = self.reader.group_by_column(data, 'continent')

        results = []
        for continent, records in grouped_data.items():
            if not continent:  # Пропускаем пустые значения
                continue

            total_population = 0
            for record in records:
                try:
                    population_str = str(record['population']).replace(',', '').strip()
                    population_value = float(population_str)
                    total_population += population_value
                except (ValueError, KeyError):
                    continue

            if total_population > 0:
                # Округляем до миллионов для читаемости
                results.append((continent, round(total_population, 2)))

        return results


# Реестр процессоров для легкого добавления новых отчетов
PROCESSORS_REGISTRY = {
    'average-gdp': AverageGDPProcessor,
    'average-unemployment': AverageUnemploymentProcessor,
    'population-by-continent': PopulationByContinentProcessor,
}


def get_processor(report_name: str) -> ReportProcessor:
    """
    Фабричная функция для получения процессора по имени отчета

    Args:
        report_name: название отчета

    Returns:
        Экземпляр ReportProcessor

    Raises:
        ValueError: если отчет не найден
    """
    processor_class = PROCESSORS_REGISTRY.get(report_name)
    if not processor_class:
        raise ValueError(f"Неизвестный тип отчета: {report_name}")
    return processor_class()
