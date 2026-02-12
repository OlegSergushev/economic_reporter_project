# Economic Data Reporter

## Оглавление

- [Что это за проект?](#what-is-this-project)
- [Для чего это нужно?](#why-need-it)
- [Структура проекта](#project-structure)
- [Как установить и запустить](#installation-and-usage)
- [Что умеет прямо сейчас?](#features)
- [Как выглядит отчет?](#example-output)

## Что это за проект?#what-is-this-project

Economic Data Reporter — это консольный инструмент на Python для обработки и анализа макроэкономических данных из CSV файлов.

Простыми словами: Вы даете скрипту CSV файлы с экономическими показателями стран, а он возвращает вам красиво оформленный отчет со средними значениями (ВВП, безработица, население по континентам).

## Для чего это нужно? {#why-need-it}

### Проблема:
У вас есть десятки CSV файлов с экономической статистикой разных стран за разные годы. Вручную открывать Excel, считать средние значения, сортировать и оформлять отчеты — долго и муторно.

### Решение:
Одна команда в терминале — и скрипт:

1. Читает все переданные файлы

2. Объединяет данные по странам

3. Вычисляет средние значения

4. Сортирует по убыванию

5. Выводит аккуратную таблицу в консоль

## Структура проекта: {#project-structure}
```bash
economic_data_reporter/
├── economic_reporter/         # Основной пакет
│   ├── cli.py                 # Парсинг аргументов командной строки
│   ├── reader.py              # Чтение и обработка CSV файлов
│   ├── processors.py          # Процессоры для разных отчетов
│   ├── formatter.py           # Форматирование таблиц и вывод
│   └── main.py                # Точка входа
├── tests/                     # Тесты (pytest)
├── data/                      # Примеры CSV файлов
├── docs/                      # Cкриншоты
├── setup.py                   # Установка пакета
└── README.md                  # Вы здесь
```

## Как установить и запустить: {#installation-and-usage}

1. Клонируйте репозиторий
```
git clone https://github.com/OlegSergushev/economic_data_reporter
cd economic_data_reporter
```
2. Запустите на тестовых данных
```
python -m economic_reporter.main --files data/economic1.csv data/economic2.csv --report average-gdp
```
3. Пробуем другие отчеты
```
python -m economic_reporter.main --files data/economic1.csv data/economic2.csv --report average-unemployment
python -m economic_reporter.main --files data/economic1.csv data/economic2.csv --report population-by-continent
```

## Что умеет прямо сейчас? {#features}

### Доступные отчеты:
- average-gdp	Средний ВВП по странам
- average-unemployment	Средняя безработица по странам
- population-by-continent	Суммарное население по континентам

## Как выглядит отчет? {#example-output}
```bash
Отчет: average-gdp
+----+-----------------+------------+
| №  | country         |        gdp |
+----+-----------------+------------+
|  1 | United States   |   23923.67 |
|  2 | China           |   17810.33 |
|  3 | Japan           |    4467.00 |
|  4 | Germany         |    4138.33 |
|  5 | India           |    3423.67 |
|  6 | United Kingdom  |    3113.33 |
|  ... | ...           |        ... |
+----+-----------------+------------+

Итоги:
• Количество записей: 20
• Максимальное значение: United States (23923.67)
• Минимальное значение: Switzerland (845.00)
```
