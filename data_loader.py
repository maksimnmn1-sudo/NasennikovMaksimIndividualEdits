"""
модуль для загрузки и подготовки данных из csv файла
преобразует данные в удобный формат для анализа
"""

import pandas as pd
from datetime import datetime
import warnings

# отключаем предупреждения
warnings.filterwarnings('ignore')


def load_and_prepare_data(filepath):
    """загружает и подготавливает данные из csv файла"""

    # загружаем данные из csv
    df = pd.read_csv(filepath)

    # преобразуем дату в формат datetime
    df['Order Date'] = pd.to_datetime(df['Order Date'])

    # создаем дополнительные временные столбцы для анализа
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.month
    df['Week'] = df['Order Date'].dt.isocalendar().week
    df['Day'] = df['Order Date'].dt.day
    df['Quarter'] = df['Order Date'].dt.quarter

    # создаем столбец год-месяц для группировки
    df['YearMonth'] = df['Order Date'].dt.to_period('M')

    # выводим общую статистику по данным
    print(f"ОБЩАЯ СТАТИСТИКА:")
    print(40 * "-")
    print(f"Загружено строк: {len(df)}")
    print(f"Период данных: {df['Order Date'].min().date()} - {df['Order Date'].max().date()}")
    print(f"Общая выручка: {df['Amount'].sum():,.0f} $")
    print(f"Общая прибыль: {df['Profit'].sum():,.0f} $")
    print(f"Количество заказов: {df['Order ID'].nunique()}")

    return df