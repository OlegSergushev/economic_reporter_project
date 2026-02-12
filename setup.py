from setuptools import setup, find_packages


setup(
    name="economic_reporter",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[],  # Нет зависимостей для работы

    # Зависимости для разработки
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'black>=23.11.0',
            'isort>=5.12.0',
            'flake8>=6.1.0',
            'mypy>=1.7.0',
        ],
    },

    python_requires='>=3.7',
)
