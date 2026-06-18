# it_gorod
Проект представляет собой Enterprise-grade ETL-решение для консолидации, очистки, трансформации и загрузки данных из гетерогенных источников в хранилище данных (DWH). Система предназначена для построения единого источника достоверных данных для бизнес-аналитики и принятия управленческих решений.
# ETL Pipeline Project

## Обзор
Проект реализует сквозной ETL-пайплайн для извлечения данных из множества источников (CSV, JSON, XLSX, XML), их трансформации и загрузки в PostgreSQL, а также построения DWH модели для аналитики.

## Особенности
- Извлечение данных из разных форматов (CSV, JSON, XLSX, XML)
- Проверка качества данных и валидация
- Обработка ошибок и логирование
- Модель DWH в виде Star Schema
- Готовые SQL-запросы для аналитики
- Автоматическая генерация тестовых данных

## Структура проекта
```
project/
├── src/ # Исходный код
│ ├── etl_pipeline.py # Основная логика ETL
│ ├── dwh_builder.py # Построитель DWH модели
│ ├── config.py # Конфигурация
│ └── utils.py # Вспомогательные функции
│
├── sql/ # SQL скрипты
│ ├── analytics.sql # Аналитические запросы
│ └── ddl.sql # Схема базы данных
│
├── data/ # Файлы данных
│ ├── customers.csv # Данные клиентов
│ ├── orders.json # Данные заказов
│ ├── products.xlsx # Данные товаров
│ ├── events.xml # Данные событий
│ └── payments.csv # Данные платежей
│
├── logs/ # Логи
│ └── etl.log # Лог-файл ETL процесса
│
├── create_test_data.py # Генератор тестовых данных
├── main.py # Главный файл запуска
├── requirements.txt # Зависимости Python
├── .env # Переменные окружения
└── README.md # Документация
```
## Требования
- Python 3.10+
- PostgreSQL 15

## Установка и настройка

### 1. Установка PostgreSQL
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows
Скачайте установщик с https://www.postgresql.org/download/windows/
```

## 2. Создание базы данных
```bash
# Войдите в PostgreSQL
sudo -u postgres psql

# Создайте базу данных
CREATE DATABASE etl_db;

# Создайте пользователя (опционально)
CREATE USER etl_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE etl_db TO etl_user;

# Выйдите
\q
```
## 3. Установка Python зависимостей
```bash
pip install -r requirements.txt
```
## 4. Настройка .env файла
Создайте файл .env в корне проекта:

``` bash
env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=etl_db
DB_USER=postgres
DB_PASSWORD=your_password
DATA_PATH=./data/
LOG_FILE=./logs/etl.log
```
## Запуск проекта
Шаг 1: Генерация тестовых данных
```bash
python create_test_data.py
```
Шаг 2: Запуск ETL пайплайна
```bash
python main.py
```
Шаг 3: Выполнение аналитических запросов
Подключитесь к PostgreSQL и выполните запросы из sql/analytics.sql:
```bash
psql -d etl_db -U postgres -f sql/analytics.sql
```
## Модель DWH (Star Schema)
### Таблицы измерений
dim_customer: Информация о клиентах
dim_product: Детали товаров
dim_date: Измерение времени для анализа
dim_payment: Информация о платежах
### Таблицы фактов
fact_orders: Транзакции заказов
fact_events: События пользовательской активности
## Аналитические запросы
Доступные запросы в sql/analytics.sql:
1. Топ-10 клиентов по сумме покупок
2. Выручка по месяцам
3. Самые популярные товары
4. Последняя активность топ-5 клиентов
5. Пользователи без заказов
6. Распределение заказов по статусам
7. Анализ платежей по методам
8. Анализ поведения пользователей
9. Маржинальность продуктов
10. Сегментация клиентов
