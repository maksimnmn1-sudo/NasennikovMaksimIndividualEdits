import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import os
import random
import matplotlib.pyplot as plt

# Подтягиваю свои модули анализа
# Важно: файлы data_loader.py и папка modules/ должны лежать рядом с этим скриптом
from data_loader import load_and_prepare_data
from modules import revenue_time, category_analysis, geo_analysis, customer_analysis


# 1. Класс для честной оценки пользователем программы
class FeedbackWindow(tk.Toplevel):
    """
    Создаю отдельное всплывающее окно
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Опрос качества")
        self.geometry("350x180")
        self.resizable(False, False)  # Запрещаю менять размер, чтобы кнопка не убежала в бесконечность

        # Делаю так, чтобы это окно всегда висело поверх остальных
        # Иначе пользователь может его не заметить за графиками
        self.attributes('-topmost', True)

        # Пишу  вопрос
        lbl = tk.Label(self, text="Понравились ли Вам мои\nиндивидуальные правки?",
                       font=('Helvetica', 12, 'bold'), justify="center")
        lbl.pack(pady=30)

        # Кнопка "Да". Тут всё стандартно: нажал — закрыл окно
        self.btn_yes = ttk.Button(self, text="Да", command=self.on_agree)
        # Использую place, чтобы ставить кнопки точно по координатам, а не как попало
        self.btn_yes.place(x=60, y=110, width=80)

        # Кнопка "Нет". А вот тут начинается магия.
        self.btn_no = ttk.Button(self, text="Нет", command=self.on_disagree)
        self.btn_no.place(x=210, y=110, width=80)

        # ВЕШАЮ ЛОВУШКУ: событие <Enter> срабатывает, как только мышь наезжает на кнопку
        # Вместо нажатия вызываю функцию побега (move_button)
        self.btn_no.bind("<Enter>", self.move_button)

    def move_button(self, event):
        """
        Логика побега: генерирую случайные координаты внутри окна и телепортирую туда кнопку
        """
        # Беру размеры окна
        width = 350
        height = 180
        # И примерные размеры кнопки
        btn_w = 80
        btn_h = 30

        # Считаю новые координаты (рандомно), но с отступами чтобы кнопка не улетела за рамку
        new_x = random.randint(10, width - btn_w - 10)
        new_y = random.randint(10, height - btn_h - 10)

        # Перемещаю кнопку
        self.btn_no.place(x=new_x, y=new_y)

    def on_agree(self):
        # Если нажали "Да"
        print("Пользователь оценил правки положительно! :)")
        messagebox.showinfo("Спасибо", "Я так и знал! Рад стараться.")
        self.destroy()

    def on_disagree(self):
        # Это сработает, только если пользователь джедай и нажмет кнопку силой мысли (или через Tab).
        messagebox.showwarning("Ошибка", "Этот вариант недоступен в данной версии реальности.")


class TextRedirector:
    """
    Маленький помощник, который перехватывает всё, что летит в консоль (print),
    и перенаправляет это в текстовое поле внутри моего приложения.
    """

    def __init__(self, widget):
        self.widget = widget

    def write(self, str_val):
        # Включаю поле, пишу текст, прокручиваю вниз и снова блокирую,
        # чтобы пользователь руками там ничего не испортил
        self.widget.configure(state='normal')
        self.widget.insert("end", str_val)
        self.widget.see("end")
        self.widget.configure(state='disabled')

    def flush(self):
        # Пустышка для совместимости с системным выводом, просто чтобы не падало
        pass


class SalesAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализ продаж")
        self.root.geometry("1000x700")

        self.df = None  # Сюда потом загрузим данные

        # Навожу красоту: настраиваю шрифты и отступы
        style = ttk.Style()
        style.configure("TButton", padding=6, font=('Helvetica', 10))
        style.configure("Header.TLabel", font=('Helvetica', 12, 'bold'))

        #Собираю интерфейс

        # Верхняя панелька для загрузки
        top_frame = ttk.Frame(root, padding="10")
        top_frame.pack(side="top", fill="x")

        self.btn_load = ttk.Button(top_frame, text="Загрузить CSV файл", command=self.load_file)
        self.btn_load.pack(side="left", padx=5)

        self.lbl_status = ttk.Label(top_frame, text="Файл не выбран", foreground="gray")
        self.lbl_status.pack(side="left", padx=10)

        # Делю экран на две части: меню слева, результаты справа
        main_pane = ttk.PanedWindow(root, orient="horizontal")
        main_pane.pack(fill="both", expand=True, padx=10, pady=5)

        # Левая часть (меню)
        self.menu_frame = ttk.Frame(main_pane, padding="5")
        main_pane.add(self.menu_frame, weight=1)

        # Создаю кнопки (но пока не включаю)
        self.create_menu_buttons()

        # Правая часть (вывод логов)
        right_frame = ttk.Frame(main_pane, padding="5")
        main_pane.add(right_frame, weight=4)

        ttk.Label(right_frame, text="Журнал и результаты анализа:", font=('Helvetica', 10, 'bold')).pack(anchor="w")

        # Текстовое поле с прокруткой
        self.text_output = tk.Text(right_frame, height=20, width=60, state='disabled', font=('Consolas', 10))
        self.scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.text_output.yview)
        self.text_output.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.text_output.pack(side="left", fill="both", expand=True)

        # Подменяю стандартный вывод на свой редиректор
        sys.stdout = TextRedirector(self.text_output)

    # 2. Метод-обертка для запуска графиков и шутки
    def run_analysis_with_feedback(self, func, *args):
        """
        Вот тут вся хитрость. Сначала я запускаю серьезный график,
        а как только пользователь его закроет — запускаю свое оценочное окно.
        """
        try:
            print("Формирование графика...")
            # Запускаю функцию графика. Matplotlib тут обычно "замораживает" программу,
            # пока окно с графиком висит на экране
            func(*args)

            # Как только график закрыли, программа отмирает и идет сюда
            print("График закрыт. Самое время спросить мнение пользователя...")
            FeedbackWindow(self.root)

        except Exception as e:
            print(f"Упс, ошибка при построении графика: {e}")

    def create_menu_buttons(self):
        """
        Создаю кнопки меню
        """

        # Блок "Время"
        lbl_time = ttk.Label(self.menu_frame, text="Выручка по времени", style="Header.TLabel")
        lbl_time.pack(pady=(10, 5), anchor="w")

        self.btn_day = ttk.Button(self.menu_frame, text="По дням", state="disabled",
                                  command=lambda: self.run_analysis_with_feedback(revenue_time.plot_daily_revenue,
                                                                                  self.df))
        self.btn_day.pack(fill="x", pady=2)

        self.btn_week = ttk.Button(self.menu_frame, text="По неделям", state="disabled",
                                   command=lambda: self.run_analysis_with_feedback(revenue_time.plot_weekly_revenue,
                                                                                   self.df))
        self.btn_week.pack(fill="x", pady=2)

        self.btn_month = ttk.Button(self.menu_frame, text="По месяцам", state="disabled",
                                    command=lambda: self.run_analysis_with_feedback(revenue_time.plot_monthly_revenue,
                                                                                    self.df))
        self.btn_month.pack(fill="x", pady=2)

        # Блок "Категории"
        lbl_cat = ttk.Label(self.menu_frame, text="Категории товаров", style="Header.TLabel")
        lbl_cat.pack(pady=(20, 5), anchor="w")

        self.btn_cat_pie = ttk.Button(self.menu_frame, text="Круговая диаграмма", state="disabled",
                                      command=lambda: self.run_analysis_with_feedback(
                                          category_analysis.plot_category_revenue, self.df))
        self.btn_cat_pie.pack(fill="x", pady=2)

        self.btn_sub_rev = ttk.Button(self.menu_frame, text="Топ подкатегорий", state="disabled",
                                      command=lambda: self.run_analysis_with_feedback(
                                          category_analysis.plot_top_subcategories, self.df, 'Amount'))
        self.btn_sub_rev.pack(fill="x", pady=2)

        # Блок "География"
        lbl_geo = ttk.Label(self.menu_frame, text="География", style="Header.TLabel")
        lbl_geo.pack(pady=(20, 5), anchor="w")

        self.btn_geo_state = ttk.Button(self.menu_frame, text="Топ штатов", state="disabled",
                                        command=lambda: self.run_analysis_with_feedback(geo_analysis.plot_state_revenue,
                                                                                        self.df))
        self.btn_geo_state.pack(fill="x", pady=2)

        self.btn_geo_city = ttk.Button(self.menu_frame, text="Топ городов", state="disabled",
                                       command=lambda: self.run_analysis_with_feedback(geo_analysis.plot_city_revenue,
                                                                                       self.df))
        self.btn_geo_city.pack(fill="x", pady=2)

        # Блок "Клиенты"
        lbl_cust = ttk.Label(self.menu_frame, text="Клиенты", style="Header.TLabel")
        lbl_cust.pack(pady=(20, 5), anchor="w")

        self.btn_cust_top = ttk.Button(self.menu_frame, text="Топ-5 Клиентов", state="disabled",
                                       command=lambda: self.run_analysis_with_feedback(
                                           customer_analysis.plot_top_customers, self.df))
        self.btn_cust_top.pack(fill="x", pady=2)

        # Сохраняю ссылки на все кнопки в список, чтобы потом разом их включить
        self.analysis_buttons = [
            self.btn_day, self.btn_week, self.btn_month,
            self.btn_cat_pie, self.btn_sub_rev,
            self.btn_geo_state, self.btn_geo_city,
            self.btn_cust_top
        ]

    def load_file(self):
        # Открываю системное окно выбора файла
        file_path = filedialog.askopenfilename(
            title="Выберите файл данных",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if not file_path:
            return  # Если передумали и нажали отмену

        try:
            # Чищу лог перед новой загрузкой
            self.text_output.configure(state='normal')
            self.text_output.delete("1.0", "end")
            self.text_output.configure(state='disabled')

            print(f"Пробую загрузить файл: {file_path}...")

            # Гружу данные через внешний модуль
            self.df = load_and_prepare_data(file_path)

            # Если не упали с ошибкой - обновляю статус и включаю кнопки
            self.lbl_status.config(text=f"Загружен: {os.path.basename(file_path)}", foreground="green")
            self.enable_buttons()

            print("\nДанные на базе! Можно нажимать кнопки слева.")

        except Exception as e:
            # Если что-то пошло не так (например, файл битый)
            self.lbl_status.config(text="Ошибка загрузки", foreground="red")
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{e}")
            print(f"Критическая ошибка: {e}")

    def enable_buttons(self):
        """Пробегаюсь по списку кнопок и делаю их активными"""
        for btn in self.analysis_buttons:
            btn.config(state="normal")

    def on_close(self):
        # При закрытии возвращаю вывод обратно в консоль и убиваю окно
        sys.stdout = sys.__stdout__
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SalesAnalysisApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()