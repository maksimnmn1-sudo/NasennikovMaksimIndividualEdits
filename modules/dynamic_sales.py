"""
интерактивный анализ динамики продаж
пользователь выбирает период и метрику для анализа
"""

import matplotlib.pyplot as plt
import pandas as pd
from config import PLOT_CONFIG, TOP_N
from utils import show_plot, format_currency


def plot_dynamic_sales(df):
    """интерактивный анализ динамики продаж за произвольный период"""

    while True:
        print(
            f"\nДИНАМИКА ПРОДАЖ ЗА ПЕРИОД (доступны данные о периоде: {df['Order Date'].min().date()} - {df['Order Date'].max().date()})")
        print("-" * 30)

        # выбор метрики для анализа
        print("1. Выручка (Amount)")
        print("2. Количество заказов")
        print("3. Прибыль (Profit)")
        print("0. Назад в главное меню")

        metric_choice = input("\nВыберите метрику (0-3): ").strip()

        # возврат в главное меню
        if metric_choice == "0":
            return

        # определение метрики по выбору
        if metric_choice == "1":
            metric = 'Amount'
            metric_name = 'Выручка'
        elif metric_choice == "2":
            metric = 'Order ID'
            metric_name = 'Количество заказов'
        elif metric_choice == "3":
            metric = 'Profit'
            metric_name = 'Прибыль'
        else:
            # по умолчанию - выручка
            print("Неверный выбор, используется выручка по умолчанию")
            metric = 'Amount'
            metric_name = 'Выручка'

        # выбор периода для группировки
        print("\nВыберите период агрегации:")
        print("1. По дням")
        print("2. По неделям")
        print("3. По месяцам")
        print("4. По кварталам")
        period_choice = input("\nВыберите период (1-4): ").strip()

        # ввод дат пользователем
        print("\nВведите период (формат ГГГГ-ММ-ДД):")
        start_date = input("Начальная дата: ").strip()
        end_date = input("Конечная дата: ").strip()

        try:
            # преобразуем строки в даты
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)

            # фильтруем данные по выбранному периоду
            mask = (df['Order Date'] >= start) & (df['Order Date'] <= end)
            filtered_df = df[mask].copy()

            # проверяем, что данные есть
            if len(filtered_df) == 0:
                print("Нет данных за выбранный период")
                input("Нажмите Enter чтобы попробовать снова...")
                continue

            # создаем столбец Period в зависимости от группировки
            if period_choice == "1":  # дни
                filtered_df['Period'] = filtered_df['Order Date'].dt.date
                xlabel = 'День'
                graph_title = f'{metric_name} за период {start_date} - {end_date}'
            elif period_choice == "2":  # недели
                filtered_df['Period'] = filtered_df['Order Date'].dt.strftime('%Y-W%W')
                xlabel = 'Неделя'
                graph_title = f'{metric_name} за период {start_date} - {end_date}'
            elif period_choice == "3":  # месяцы
                filtered_df['Period'] = filtered_df['Order Date'].dt.to_period('M')
                xlabel = 'Месяц'
                graph_title = f'{metric_name} за период {start_date} - {end_date}'
            elif period_choice == "4":  # кварталы
                filtered_df['Period'] = filtered_df['Order Date'].dt.to_period('Q')
                xlabel = 'Квартал'
                graph_title = f'{metric_name} за период {start_date} - {end_date}'
            else:
                # по умолчанию - месяцы
                print("Неверный выбор, используется месяц по умолчанию")
                filtered_df['Period'] = filtered_df['Order Date'].dt.to_period('M')
                xlabel = 'Месяц'
                graph_title = f'{metric_name} за период {start_date} - {end_date}'

            # группируем данные по периоду
            if metric == 'Order ID':
                # для заказов считаем количество уникальных id
                dynamic_data = filtered_df.groupby('Period')[metric].nunique()
            else:
                # для выручки и прибыли - суммируем
                dynamic_data = filtered_df.groupby('Period')[metric].sum()

            # создаем график
            fig, ax = plt.subplots(figsize=PLOT_CONFIG['figsize'])

            # выбираем тип графика в зависимости от периода
            if period_choice in ['1', '2']:  # дни и недели - линейный график
                ax.plot(dynamic_data.index.astype(str), dynamic_data.values,
                        color='#3498db', linewidth=2, marker='o')
            else:  # месяцы и кварталы - столбчатая диаграмма
                bars = ax.bar(dynamic_data.index.astype(str), dynamic_data.values,
                              color='#3498db', alpha=0.7)

                # добавляем значения поверх столбцов
                for bar in bars:
                    height = bar.get_height()
                    if metric == 'Order ID':
                        ax.text(bar.get_x() + bar.get_width() / 2., height,
                                f'{int(height)}',
                                ha='center', va='bottom', fontsize=8)
                    else:
                        ax.text(bar.get_x() + bar.get_width() / 2., height,
                                format_currency(height),
                                ha='center', va='bottom', fontsize=8)

            # настройки графика
            ax.set_title(graph_title, fontsize=14, fontweight='bold')
            ax.set_xlabel(xlabel)
            ax.set_ylabel(metric_name)
            ax.tick_params(axis='x', rotation=45)
            ax.grid(True, alpha=0.3)

            plt.tight_layout()
            show_plot(fig, graph_title)

            # выбор дальнейшего действия
            print("\n1. Построить другой график динамики")
            print("2. Вернуться в главное меню")

            next_action = input("\nВыберите действие (1-2): ").strip()
            if next_action == "2":
                return  # возвращаемся в главное меню

        # обработка ошибок
        except Exception as e:
            print(f"Ошибка: {e}")
            print("Убедитесь, что даты введены в правильном формате (ГГГГ-ММ-ДД)")
            input("Нажмите Enter чтобы попробовать снова...")
            continue