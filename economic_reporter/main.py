#!/usr/bin/env python3
"""
Модуль для генерации отчетов по макроэкономическим данным.
Использует только стандартную библиотеку Python.
"""

import sys
from typing import List, Tuple

from .cli import parse_args
from .processors import get_processor
from .formatter import TableFormatter


def sort_data(data: List[Tuple[str, float]], reverse: bool = True) -> List[Tuple[str, float]]:
    """Сортирует данные по значению"""
    return sorted(data, key=lambda x: x[1], reverse=reverse)


def main():
    """Основная функция приложения"""
    try:
        # Парсим аргументы
        args = parse_args()

        # Получаем процессор для отчета
        processor = get_processor(args.report)

        # Выполняем обработку
        print(f"Обработка {len(args.files)} файлов...")
        results = processor.execute(args.files)

        if not results:
            print("Нет данных для отображения. Проверьте входные файлы.")
            sys.exit(1)

        # Сортируем результаты
        reverse_sort = args.sort == 'desc'
        sorted_results = sort_data(results, reverse_sort)

        # Применяем лимит, если указан
        if args.limit and args.limit > 0:
            sorted_results = sorted_results[:args.limit]

        # Форматируем и выводим отчет
        report = TableFormatter.format_report(args.report, sorted_results)
        print(report)

    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
