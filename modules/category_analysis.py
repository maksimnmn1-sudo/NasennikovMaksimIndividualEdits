"""
анализ категорий и подкатегорий товаров
круговые диаграммы и топы по выручке/прибыли
"""

import matplotlib.pyplot as plt
import pandas as pd
from config import PLOT_CONFIG, TOP_N
from utils import show_plot, format_currency


def plot_category_revenue(df):
    """круговая диаграмма выручки по категориям товаров"""

    # группируем по категориям, суммируем выручку
    category_revenue = df.groupby('Category')['Amount'].sum()

    # создаем квадратный график для круговой диаграммы
    fig, ax = plt.subplots(figsize=(8, 8))

    # цвета для секторов
    colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']

    # рисуем круговую диаграмму
    wedges, texts, autotexts = ax.pie(category_revenue.values,
                                      labels=category_revenue.index,
                                      autopct='%1.1f%%',
                                      colors=colors,
                                      startangle=90)

    ax.set_title('Распределение выручки по категориям',
                 fontsize=14, fontweight='bold')

    # настраиваем отображение процентов
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')

    plt.tight_layout()
    show_plot(fig, 'Выручка по категориям (круговая диаграмма)')


def plot_top_subcategories(df, metric='Amount'):
    """топ-5 подкатегорий товаров по выручке или прибыли"""

    # определяем заголовок и цвет в зависимости от метрики
    if metric == 'Amount':
        title = 'Топ-5 подкатегорий по выручке'
        color = '#3498db'  # синий
    else:  # metric == 'Profit'
        title = 'Топ-5 подкатегорий по прибыли'
        color = '#2ecc71'  # зеленый

    # группируем по подкатегориям, суммируем метрику
    subcategory_data = df.groupby('Sub-Category')[metric].sum()

    # берем топ-5, сортируем по возрастанию
    top_5 = subcategory_data.nlargest(TOP_N).sort_values()

    fig, ax = plt.subplots(figsize=(10, 6))

    # рисуем горизонтальные столбцы
    bars = ax.barh(top_5.index.astype(str), top_5.values,
                   color=color, alpha=0.7)

    # добавляем значения на столбцы
    for bar in bars:
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height() / 2,
                format_currency(width),
                ha='left', va='center', fontsize=10)

    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Сумма ($)')
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    show_plot(fig, title)