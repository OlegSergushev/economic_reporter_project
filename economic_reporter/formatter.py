from typing import List, Tuple


class TableFormatter:
    """Класс для форматирования табличного вывода"""

    @staticmethod
    def format_table(data: List[Tuple[str, float]],
                     headers: Tuple[str, str] = ('country', 'gdp')) -> str:
        """
        Форматирует данные в виде таблицы с нумерацией строк

        Args:
            data: список кортежей (ключ, значение)
            headers: заголовки колонок

        Returns:
            Отформатированная таблица в виде строки
        """
        if not data:
            return "Нет данных для отображения"

        # Определяем максимальные длины
        max_country_len = max(len(str(country)) for country, _ in data)
        max_country_len = max(max_country_len, len(headers[0]))

        # Для индекса (номера строки)
        max_index_len = len(str(len(data)))
        max_index_len = max(max_index_len, 1)  # Минимум 1 для "№"

        # Для значения (GDP, unemployment и т.д.)
        value_header = headers[1]

        # Создаем границу
        border = TableFormatter._create_border(max_index_len, max_country_len)

        # Собираем таблицу
        lines = list()
        lines.append(border)
        lines.append(TableFormatter._format_header_row(max_index_len, max_country_len, value_header))
        lines.append(border)

        for i, (country, value) in enumerate(data, 1):
            lines.append(TableFormatter._format_data_row(i, country, value, max_index_len, max_country_len))

        lines.append(border)

        return '\n'.join(lines)

    @staticmethod
    def _create_border(max_index_len: int, max_country_len: int) -> str:
        """Создает границу таблицы"""
        return f"+{'─' * (max_index_len + 2)}+{'─' * (max_country_len + 2)}+{'─' * 12}+"

    @staticmethod
    def _format_header_row(max_index_len: int, max_country_len: int, value_header: str) -> str:
        """Форматирует строку заголовка"""
        return f"| {'№':>{max_index_len}} | {'country':<{max_country_len}} | {value_header:>10} |"

    @staticmethod
    def _format_data_row(index: int, country: str, value: float, max_index_len: int, max_country_len: int) -> str:
        """Форматирует строку данных"""
        return f"| {index:>{max_index_len}} | {country:<{max_country_len}} | {value:>10.2f} |"

    @staticmethod
    def format_report(report_name: str, data: List[Tuple[str, float]]) -> str:
        """
        Формирует полный отчет с заголовком

        Args:
            report_name: название отчета
            data: данные для отображения

        Returns:
            Полный отчет в виде строки
        """
        # Маппинг заголовков для разных типов отчетов
        headers_map = {
            'average-gdp': 'gdp',
            'average-unemployment': 'unemployment',
            'population-by-continent': 'population',
        }

        value_header = headers_map.get(report_name, 'value')

        # Формируем отчет
        report_lines = [
            f"\nОтчет: {report_name}",
            TableFormatter.format_table(data, ('country', value_header))
        ]

        # Добавляем статистику
        if data:
            max_item = max(data, key=lambda x: x[1])
            min_item = min(data, key=lambda x: x[1])
            report_lines.extend([
                f"\nИтоги:",
                f"• Количество записей: {len(data)}",
                f"• Максимальное значение: {max_item[0]} ({max_item[1]:.2f})",
                f"• Минимальное значение: {min_item[0]} ({min_item[1]:.2f})"
            ])

        return '\n'.join(report_lines)
