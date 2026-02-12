import pytest
import tempfile
import csv
from pathlib import Path

from economic_reporter.reader import CSVReader
from economic_reporter.processors import (
    AverageGDPProcessor,
    AverageUnemploymentProcessor,
    PopulationByContinentProcessor,
    get_processor
)
from economic_reporter.formatter import TableFormatter
from economic_reporter.cli import parse_args


class TestCSVReader:
    """Тесты для CSVReader"""

    def test_read_valid_csv(self):
        """Тест чтения корректного CSV файла"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['country', 'gdp', 'year'])
            writer.writeheader()
            writer.writerow({'country': 'USA', 'gdp': '25000', 'year': '2023'})
            writer.writerow({'country': 'China', 'gdp': '18000', 'year': '2023'})
            temp_path = f.name

        reader = CSVReader()
        data = reader.read_files([temp_path])

        assert len(data) == 2
        assert data[0]['country'] == 'USA'
        assert data[1]['country'] == 'China'

        Path(temp_path).unlink()

    def test_read_multiple_files(self):
        """Тест чтения нескольких файлов"""
        # Создаем временные файлы
        temp_files = []
        for i in range(2):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                writer = csv.DictWriter(f, fieldnames=['country', 'gdp'])
                writer.writeheader()
                writer.writerow({'country': f'Country{i}', 'gdp': str(1000 + i)})
                temp_files.append(f.name)

        reader = CSVReader()
        data = reader.read_files(temp_files)

        assert len(data) == 2

        # Удаляем временные файлы
        for path in temp_files:
            Path(path).unlink()

    def test_required_columns_check(self):
        """Тест проверки необходимых колонок"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['country', 'year'])
            writer.writeheader()
            writer.writerow({'country': 'USA', 'year': '2023'})
            temp_path = f.name

        reader = CSVReader(required_columns=['country', 'gdp'])

        with pytest.raises(ValueError, match="не содержит колонок"):
            reader.read_files([temp_path])

        Path(temp_path).unlink()

    def test_group_by_column_static_method(self):
        """Тест статического метода группировки"""
        data = [
            {'country': 'USA', 'gdp': '25000'},
            {'country': 'USA', 'gdp': '26000'},
            {'country': 'China', 'gdp': '18000'},
        ]

        # Вызываем как статический метод
        grouped = CSVReader.group_by_column(data, 'country')

        assert 'USA' in grouped
        assert 'China' in grouped
        assert len(grouped['USA']) == 2
        assert len(grouped['China']) == 1

    def test_read_files_file_not_found(self):
        """Тест обработки ошибки - файл не найден"""
        reader = CSVReader()

        with pytest.raises(FileNotFoundError, match="Файл не найден"):
            reader.read_files(["non_existent_file.csv"])

    def test_read_files_general_exception(self, monkeypatch):
        """Тест обработки общей ошибки при чтении файла"""

        def mock_open(*_, **__):
            raise PermissionError("Нет доступа к файлу")

        monkeypatch.setattr("builtins.open", mock_open)

        reader = CSVReader()
        with pytest.raises(RuntimeError, match="Ошибка при чтении файла"):
            reader.read_files(["test.csv"])

    def test_extract_numeric_column(self):
        """Тест извлечения числовых значений по колонке"""
        data = [
            {'country': 'USA', 'gdp': '25000'},
            {'country': 'USA', 'gdp': 'invalid'},  # Должно быть пропущено
            {'country': 'China', 'gdp': '18000'},
        ]

        result = CSVReader.extract_numeric_column(data, 'gdp')

        assert 'USA' in result
        assert 'China' in result
        assert len(result['USA']) == 1  # invalid пропущен
        assert result['USA'][0] == 25000.0


class TestProcessors:
    """Тесты для процессоров отчетов"""

    @pytest.fixture
    def sample_data(self):
        """Fixture с тестовыми данными"""

        return [
            {'country': 'USA', 'gdp': '25000', 'unemployment': '3.5', 'population': '350',
             'continent': 'North America'},
            {'country': 'USA', 'gdp': '26000', 'unemployment': '3.7', 'population': '351',
             'continent': 'North America'},
            {'country': 'China', 'gdp': '18000', 'unemployment': '5.2', 'population': '1425', 'continent': 'Asia'},
        ]

    def test_average_gdp_processor(self, sample_data):
        """Тест процессора среднего ВВП"""
        processor = AverageGDPProcessor()
        results = processor.process(sample_data)

        # Проверяем что есть 2 страны
        assert len(results) == 2

        # Проверяем расчет среднего для USA
        usa_gdp = [result[1] for result in results if result[0] == 'USA'][0]
        assert usa_gdp == pytest.approx(25500.0)

    def test_average_unemployment_processor(self, sample_data):
        """Тест процессора средней безработицы"""
        processor = AverageUnemploymentProcessor()
        results = processor.process(sample_data)

        assert len(results) == 2

        # Проверяем расчет для USA
        usa_unemployment = [result[1] for result in results if result[0] == 'USA'][0]
        assert usa_unemployment == pytest.approx(3.6)

    def test_population_by_continent_processor(self, sample_data):
        """Тест процессора населения по континентам"""
        processor = PopulationByContinentProcessor()
        results = processor.process(sample_data)

        assert len(results) == 2

        # Проверяем сумму населения для North America
        na_population = [result[1] for result in results if result[0] == 'North America'][0]
        assert na_population == pytest.approx(701.0)

    def test_get_processor_valid(self):
        """Тест получения валидного процессора"""
        processor = get_processor('average-gdp')
        assert isinstance(processor, AverageGDPProcessor)

    def test_get_processor_invalid(self):
        """Тест получения невалидного процессора"""
        with pytest.raises(ValueError, match="Неизвестный тип отчета"):
            get_processor('invalid-report')

    def test_average_gdp_processor_with_invalid_data(self):
        """Тест процессора с некорректными данными"""
        data = [
            {'country': 'USA', 'gdp': '25000'},
            {'country': 'USA', 'gdp': 'invalid'},  # Некорректное значение
            {'country': 'USA', 'gdp': ''},  # Пустое значение
            {'country': 'China', 'gdp': '18000'},
        ]

        processor = AverageGDPProcessor()
        results = processor.process(data)

        # Должен обработать только валидные записи
        usa_gdp = [r[1] for r in results if r[0] == 'USA'][0]
        assert usa_gdp == 25000.0  # Только одна валидная запись

    def test_get_processor_invalid_report(self):
        """Тест получения невалидного процессора"""
        with pytest.raises(ValueError, match="Неизвестный тип отчета"):
            get_processor("non-existent-report")

    def test_processors_with_empty_data(self):
        """Тест процессоров с пустыми данными"""
        processor = AverageGDPProcessor()
        results = processor.process([])
        assert results == []


class TestTableFormatter:
    """Тесты для форматирования таблиц"""

    def test_format_table_empty(self):
        """Тест форматирования пустой таблицы"""
        result = TableFormatter.format_table([])
        assert result == "Нет данных для отображения"

    def test_format_table_with_data(self):
        """Тест форматирования таблицы с данными"""
        data = [('USA', 25500.50), ('China', 18000.75)]
        result = TableFormatter.format_table(data)

        assert 'USA' in result
        assert 'China' in result
        assert '25500.50' in result
        assert '18000.75' in result
        assert '|' in result  # Проверяем наличие границ таблицы

    def test_format_table_empty_data(self):
        """Тест форматирования пустой таблицы"""
        result = TableFormatter.format_table([])
        assert result == "Нет данных для отображения"

    def test_format_report_different_types(self):
        """Тест форматирования разных типов отчетов"""
        data = [('USA', 25500.50), ('China', 18000.75)]

        # Тест для average-gdp
        report1 = TableFormatter.format_report('average-gdp', data)
        assert 'country' in report1
        assert 'gdp' in report1

        # Тест для неизвестного типа
        report3 = TableFormatter.format_report('unknown', data)
        assert 'item' in report3
        assert 'value' in report3

    def test_format_report(self):
        """Тест форматирования полного отчета"""
        data = [('USA', 25500.50), ('China', 18000.75)]
        result = TableFormatter.format_report('average-gdp', data)

        assert 'Отчет: average-gdp' in result
        assert 'Итоги:' in result
        assert 'Количество записей: 2' in result

    def test_format_table_with_index(self):
        """Тест форматирования таблицы с нумерацией строк"""
        data = [('USA', 25500.50), ('China', 18000.75)]
        result = TableFormatter.format_table(data, ('country', 'gdp'))

        assert '| № |' in result
        assert '| 1 | USA' in result
        assert '| 2 | China' in result


class TestCLI:
    """Тесты для командной строки"""

    def test_parse_args_valid(self):
        """Тест валидных аргументов"""
        args = ['--files', 'data.csv', '--report', 'average-gdp']
        result = parse_args(args)

        assert result.files == ['data.csv']
        assert result.report == 'average-gdp'
        assert result.sort == 'desc'

    def test_parse_args_with_sort(self):
        """Тест аргументов с сортировкой"""
        args = ['--files', 'data.csv', '--report', 'average-gdp', '--sort', 'asc']
        result = parse_args(args)

        assert result.sort == 'asc'

    def test_parse_args_with_limit(self):
        """Тест аргументов с лимитом"""
        args = ['--files', 'data.csv', '--report', 'average-gdp', '--limit', '5']
        result = parse_args(args)

        assert result.limit == 5

    def test_parse_args_missing_required(self):
        """Тест отсутствия обязательных аргументов"""
        with pytest.raises(SystemExit):
            parse_args(['--files', 'data.csv'])  # Нет --report

    def test_parse_args_invalid_report(self):
        """Тест невалидного отчета"""
        with pytest.raises(SystemExit):
            parse_args(['--files', 'data.csv', '--report', 'invalid'])


class TestMain:
    """Тесты для main.py"""

    def test_main_success(self, monkeypatch, tmp_path):
        """Тест успешного выполнения main"""
        # Создаем тестовый CSV файл
        csv_file = tmp_path / "test.csv"
        with open(csv_file, 'w') as f:
            f.write("country,gdp\n")
            f.write("USA,25000\n")
            f.write("China,18000\n")

        # Подменяем аргументы командной строки
        test_args = [
            'main.py',
            '--files', str(csv_file),
            '--report', 'average-gdp'
        ]
        monkeypatch.setattr('sys.argv', test_args)

        # Импортируем и запускаем main
        from economic_reporter.main import main
        main()  # Не должно быть исключений

    def test_main_no_data(self, monkeypatch):
        """Тест main с отсутствием данных"""
        test_args = [
            'main.py',
            '--files', 'nonexistent.csv',
            '--report', 'average-gdp'
        ]
        monkeypatch.setattr('sys.argv', test_args)

        from economic_reporter.main import main
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1
