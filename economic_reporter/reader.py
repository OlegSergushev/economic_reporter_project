import csv
from collections import defaultdict
from typing import List, Dict, Any, DefaultDict


class CSVReader:
    """Класс для чтения и обработки CSV файлов"""

    def __init__(self, required_columns: List[str] = None):
        self.required_columns = required_columns or []

    def read_files(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Читает и объединяет данные из нескольких CSV файлов

        Args:
            file_paths: список путей к CSV файлам

        Returns:
            Список словарей с данными из всех файлов
        """
        all_data = []

        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)

                    # Проверяем наличие необходимых колонок
                    if self.required_columns:
                        missing_columns = [
                            col for col in self.required_columns
                            if col not in reader.fieldnames
                        ]
                        if missing_columns:
                            raise ValueError(
                                f"Файл {file_path} не содержит колонок: {missing_columns}"
                            )

                    # Читаем данные
                    file_data = list(reader)
                    all_data.extend(file_data)

            except FileNotFoundError:
                raise FileNotFoundError(f"Файл не найден: {file_path}")
            except ValueError:
                raise
            except Exception as e:
                raise RuntimeError(f"Ошибка при чтении файла {file_path}: {e}")

        return all_data

    @staticmethod
    def group_by_column(data: List[Dict[str, Any]], column: str) -> DefaultDict[str, List[Dict[str, Any]]]:
        """
        Группирует данные по указанной колонке

        Args:
            data: список словарей с данными
            column: название колонки для группировки

        Returns:
            Словарь {значение_колонки: [список_записей]}
        """
        grouped = defaultdict(list)
        for row in data:
            key = row.get(column)
            if key is not None:
                grouped[key].append(row)
        return grouped

    @staticmethod
    def extract_numeric_column(data: List[Dict[str, Any]], column: str) -> Dict[str, List[float]]:
        """
        Извлекает числовые значения из указанной колонки, сгруппированные по ключевой колонке

        Args:
            data: список словарей с данными
            column: название числовой колонки для извлечения

        Returns:
            Словарь {группа: [список_чисел]}
        """
        # Этот метод требует наличия колонки 'country' как ключа группировки
        grouped_values = defaultdict(list)

        for row in data:
            group_key = row.get('country')  # Предполагаем, что группируем по странам
            if group_key and column in row:
                try:
                    value_str = str(row[column]).replace(',', '').strip()
                    value = float(value_str)
                    grouped_values[group_key].append(value)
                except (ValueError, KeyError):
                    continue

        return grouped_values
