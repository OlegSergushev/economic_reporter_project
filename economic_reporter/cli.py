import argparse
from typing import List


def parse_args(args: List[str] = None):
    """
    Парсит аргументы командной строки

    Args:
        args: список аргументов (если None, берется из sys.argv)

    Returns:
        Namespace с аргументами
    """
    parser = argparse.ArgumentParser(
        description='Генератор отчетов по макроэкономическим данным',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main.py --files data1.csv data2.csv --report average-gdp
  python main.py --files dataset.csv --report average-unemployment
  python main.py --files *.csv --report population-by-continent

Доступные отчеты:
  average-gdp             - Средний ВВП по странам
  average-unemployment    - Средняя безработица по странам
  population-by-continent - Население по континентам
        """
    )

    parser.add_argument(
        '--files',
        nargs='+',
        required=True,
        help='Список CSV файлов для обработки'
    )

    parser.add_argument(
        '--report',
        required=True,
        choices=['average-gdp', 'average-unemployment', 'population-by-continent'
                                                        ''],
        help='Тип отчета для генерации'
    )

    parser.add_argument(
        '--sort',
        choices=['asc', 'desc'],
        default='desc',
        help='Порядок сортировки (по умолчанию: desc)'
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Ограничить количество выводимых записей'
    )

    return parser.parse_args(args)
