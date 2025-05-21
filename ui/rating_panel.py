import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import sys

# Добавляем родительскую директорию в путь поиска модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database
from rating_system import HotelRatingSystem


class RatingPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.db = Database()
        self.rating_system = HotelRatingSystem()

        # Получаем все категории и критерии из базы данных
        self.categories = self.db.get_rating_criteria()

        # Текущая категория для оценки (индекс)
        self.current_category_idx = 0

        # Словари для хранения оценок
        self.category_ratings = {}
        self.criteria_ratings = {}

        # Обработчик события завершения оценки
        self.on_rating_complete = None

        # Создаем интерфейс
        self.create_widgets()

        # Отображаем первую категорию
        self.show_category(0)

    def create_widgets(self):
        """Создание виджетов панели оценки."""
        # Верхняя часть - выбор категории
        self.header_frame = ttk.Frame(self)
        self.header_frame.pack(fill=tk.X, pady=(0, 10))

        self.title_label = ttk.Label(self.header_frame, text="Оценка отеля",
                                     style="Title.TLabel")
        self.title_label.pack(pady=10)

        # Полоса прогресса
        self.progress_frame = ttk.Frame(self.header_frame)
        self.progress_frame.pack(fill=tk.X, padx=20, pady=5)

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var,
                                            length=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X)

        # Фрейм для навигации по категориям
        self.nav_frame = ttk.Frame(self.header_frame)
        self.nav_frame.pack(fill=tk.X, padx=20, pady=5)

        # Создаем кнопки для каждой категории
        self.category_buttons = []

        for i, category in enumerate(self.categories):
            btn = ttk.Button(self.nav_frame, text=category['name'].split('_')[-1].capitalize(),
                             command=lambda idx=i: self.show_category(idx),
                             width=15)
            btn.pack(side=tk.LEFT, padx=5)
            self.category_buttons.append(btn)

        # Обновляем стиль для активной категории
        self.update_category_buttons()

        # Центральная часть - критерии для оценки
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Заголовок категории
        self.category_frame = ttk.Frame(self.content_frame)
        self.category_frame.pack(fill=tk.X, pady=(0, 10))

        self.category_label = ttk.Label(self.category_frame, text="",
                                        style="Subtitle.TLabel")
        self.category_label.pack(side=tk.LEFT)

        self.category_description = ttk.Label(self.category_frame, text="")
        self.category_description.pack(side=tk.LEFT, padx=(10, 0))

        # Фрейм для критериев
        self.criteria_canvas = tk.Canvas(self.content_frame, highlightthickness=0)
        self.criteria_scrollbar = ttk.Scrollbar(self.content_frame,
                                                orient="vertical",
                                                command=self.criteria_canvas.yview)
        self.criteria_scrollframe = ttk.Frame(self.criteria_canvas)

        self.criteria_scrollframe.bind(
            "<Configure>",
            lambda e: self.criteria_canvas.configure(
                scrollregion=self.criteria_canvas.bbox("all")
            )
        )

        self.criteria_canvas.create_window((0, 0), window=self.criteria_scrollframe, anchor="nw")
        self.criteria_canvas.configure(yscrollcommand=self.criteria_scrollbar.set)

        self.criteria_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.criteria_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Нижняя часть - кнопки
        self.buttons_frame = ttk.Frame(self)
        self.buttons_frame.pack(fill=tk.X, pady=10, padx=20)

        self.prev_button = ttk.Button(self.buttons_frame, text="Назад",
                                      command=self.go_to_prev_category)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.next_button = ttk.Button(self.buttons_frame, text="Продолжить",
                                      command=self.go_to_next_category,
                                      style="Primary.TButton")
        self.next_button.pack(side=tk.RIGHT, padx=5)

        # Словарь для хранения виджетов критериев
        self.criteria_widgets = {}

    def show_category(self, category_idx):
        """Отображение выбранной категории для оценки."""
        if category_idx < 0 or category_idx >= len(self.categories):
            return

        self.current_category_idx = category_idx
        category = self.categories[category_idx]

        # Обновляем заголовок категории
        category_name_ru = self.get_category_name_ru(category['name'])
        self.category_label.config(text=category_name_ru)
        self.category_description.config(text=category['description'] or "")

        # Обновляем стиль кнопок категорий
        self.update_category_buttons()

        # Очищаем предыдущие критерии
        for widget in self.criteria_scrollframe.winfo_children():
            widget.destroy()

        self.criteria_widgets = {}

        # Отображаем критерии для текущей категории
        for i, criteria in enumerate(category['criteria']):
            criteria_frame = ttk.Frame(self.criteria_scrollframe)
            criteria_frame.pack(fill=tk.X, pady=(0, 10))

            # Название критерия
            criteria_name_label = ttk.Label(criteria_frame, text=criteria['name'],
                                            font=("Arial", 11, "bold"))
            criteria_name_label.grid(row=0, column=0, sticky="w", padx=5)

            # Описание критерия
            if criteria['description']:
                criteria_desc_label = ttk.Label(criteria_frame, text=criteria['description'])
                criteria_desc_label.grid(row=1, column=0, sticky="w", padx=5, pady=(0, 5))

            # Шкала для оценки (от 0 до 5)
            scale_frame = ttk.Frame(criteria_frame)
            scale_frame.grid(row=2, column=0, sticky="ew", padx=5)

            # Добавляем метки для значений шкалы
            scale_labels_frame = ttk.Frame(scale_frame)
            scale_labels_frame.pack(fill=tk.X)

            ttk.Label(scale_labels_frame, text="0", width=3).pack(side=tk.LEFT)
            ttk.Label(scale_labels_frame, text="2.5", width=3).pack(side=tk.LEFT, padx=(91, 0))
            ttk.Label(scale_labels_frame, text="5", width=3).pack(side=tk.RIGHT)

            # Шкала
            scale_var = tk.DoubleVar(value=2.5)  # Начальное значение - 2.5
            criteria_scale = ttk.Scale(scale_frame, from_=0, to=5,
                                       orient="horizontal",
                                       variable=scale_var,
                                       length=200)
            criteria_scale.pack(fill=tk.X, pady=(0, 5))

            # Текущее значение
            value_frame = ttk.Frame(scale_frame)
            value_frame.pack(fill=tk.X)

            value_label = ttk.Label(value_frame, text="Текущая оценка:")
            value_label.pack(side=tk.LEFT)

            value_var = tk.StringVar(value="5")
            value_display = ttk.Label(value_frame, textvariable=value_var,
                                      width=3, font=("Arial", 10, "bold"))
            value_display.pack(side=tk.LEFT, padx=5)

            # Обновление значения при изменении шкалы
            def update_value(val, var=value_var):
                var.set(str(int(float(val))))

            criteria_scale.config(command=lambda val, v=value_var: update_value(val, v))

            # Сохраняем ссылки на виджеты
            self.criteria_widgets[criteria['id']] = {
                'scale': criteria_scale,
                'var': scale_var,
                'value_var': value_var,
                'criteria_info': criteria
            }

            # Проверяем, была ли уже оценка для этого критерия
            category_key = category['name']
            criteria_key = criteria['name']

            if (category_key in self.criteria_ratings and
                    criteria_key in self.criteria_ratings[category_key]):
                saved_value = self.criteria_ratings[category_key][criteria_key]
                scale_var.set(saved_value)
                value_var.set(str(int(saved_value)))

        # Обновляем состояние кнопок навигации
        self.update_navigation_buttons()

        # Обновляем прогресс
        self.update_progress()

    def update_category_buttons(self):
        """Обновление стиля кнопок категорий."""
        for i, btn in enumerate(self.category_buttons):
            if i < self.current_category_idx:
                # Оцененные категории
                btn.state(["!disabled"])
                btn.configure(style="Secondary.TButton")
            elif i == self.current_category_idx:
                # Текущая категория
                btn.state(["!disabled"])
                btn.configure(style="Primary.TButton")
            else:
                # Не оцененные категории
                btn.state(["!disabled"])
                btn.configure(style="Secondary.TButton")

    def update_navigation_buttons(self):
        """Обновление состояния кнопок навигации."""
        # Кнопка "Назад"
        if self.current_category_idx == 0:
            self.prev_button.state(["disabled"])
        else:
            self.prev_button.state(["!disabled"])

        # Кнопка "Продолжить"/"Завершить"
        if self.current_category_idx == len(self.categories) - 1:
            self.next_button.configure(text="Завершить")
        else:
            self.next_button.configure(text="Продолжить")

    def update_progress(self):
        """Обновление полосы прогресса."""
        progress = (self.current_category_idx) / len(self.categories) * 100
        self.progress_var.set(progress)

    def go_to_prev_category(self):
        """Переход к предыдущей категории."""
        if self.current_category_idx > 0:
            # Сохраняем текущие оценки
            self.save_current_ratings()

            # Переходим к предыдущей категории
            self.show_category(self.current_category_idx - 1)

    def go_to_next_category(self):
        """Переход к следующей категории или завершение оценки."""
        # Сохраняем текущие оценки
        self.save_current_ratings()

        if self.current_category_idx < len(self.categories) - 1:
            # Переходим к следующей категории
            self.show_category(self.current_category_idx + 1)
        else:
            # Завершаем оценку
            self.complete_rating()

    def save_current_ratings(self):
        """Сохранение оценок для текущей категории."""
        category = self.categories[self.current_category_idx]
        category_key = category['name']

        # Инициализируем словарь для категории, если его еще нет
        if category_key not in self.criteria_ratings:
            self.criteria_ratings[category_key] = {}

        # Сохраняем оценки по критериям
        for criteria_id, widgets in self.criteria_widgets.items():
            criteria_key = widgets['criteria_info']['name']
            rating_value = int(widgets['var'].get())
            self.criteria_ratings[category_key][criteria_key] = rating_value

        # Рассчитываем среднюю оценку для категории
        criteria_values = list(self.criteria_ratings[category_key].values())
        category_avg = sum(criteria_values) / len(criteria_values)
        self.category_ratings[category_key] = category_avg

    def complete_rating(self):
        """Завершение оценки отеля."""
        # Рассчитываем итоговую звездность
        total_rating, _ = self.rating_system.calculate_final_rating(self.category_ratings)

        # Запрашиваем название отеля
        hotel_name = simpledialog.askstring("Название отеля",
                                            "Введите название оцениваемого отеля:",
                                            parent=self)

        # Вызываем обработчик события завершения оценки
        if self.on_rating_complete:
            self.on_rating_complete(
                self.category_ratings,
                self.criteria_ratings,
                total_rating,
                hotel_name
            )

    def reset(self):
        """Сброс всех оценок и переход к первой категории."""
        self.category_ratings = {}
        self.criteria_ratings = {}
        self.current_category_idx = 0
        self.show_category(0)

    def get_category_name_ru(self, category_name):
        """Получение русского названия категории."""
        category_names = {
            'service_quality': 'Качество обслуживания',
            'infrastructure': 'Инфраструктура и удобства',
            'location': 'Местоположение',
            'dining': 'Питание и кухня',
            'room_comfort': 'Комфорт номеров'
        }

        return category_names.get(category_name, category_name)