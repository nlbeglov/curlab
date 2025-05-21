import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Добавляем родительскую директорию в путь поиска модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.rating_panel import RatingPanel
from ui.result_panel import ResultPanel
from ui.hotel_list import HotelListPanel


class HotelRatingApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Система оценки отелей 2.0")
        self.geometry("1200x800")
        self.minsize(1000, 700)

        # Настраиваем тему
        self.configure_style()

        # Создаем меню
        self.create_menu()

        # Создаем фрейм для главного контента
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Создаем notebook (вкладки)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка для оценки отеля
        self.rating_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.rating_frame, text="Оценка отеля")

        # Вкладка для просмотра списка отелей
        self.hotel_list_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.hotel_list_frame, text="Список отелей")

        # Создаем панель оценки
        self.rating_panel = RatingPanel(self.rating_frame)
        self.rating_panel.pack(fill=tk.BOTH, expand=True)

        # Создаем панель результатов
        self.result_panel = ResultPanel(self.rating_frame)

        # Создаем панель списка отелей
        self.hotel_list_panel = HotelListPanel(self.hotel_list_frame)
        self.hotel_list_panel.pack(fill=tk.BOTH, expand=True)

        # Настраиваем событие завершения оценки
        self.rating_panel.on_rating_complete = self.show_results

        # Строка состояния
        self.status_bar = ttk.Label(self, text="Готово", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def configure_style(self):
        """Настройка стиля приложения."""
        style = ttk.Style()

        # Пытаемся использовать современную тему если доступно
        try:
            style.theme_use("clam")  # можно также попробовать "alt", "default", "classic", "vista"
        except tk.TclError:
            pass

        # Настройка цветов и шрифтов
        style.configure("TLabel", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10))
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TNotebook", background="#f0f0f0")
        style.configure("TNotebook.Tab", font=("Arial", 10), padding=[10, 5])

        # Настройка заголовков
        style.configure("Title.TLabel", font=("Arial", 16, "bold"))
        style.configure("Subtitle.TLabel", font=("Arial", 12, "bold"))

        # Настройка кнопок
        style.configure("Primary.TButton", font=("Arial", 10, "bold"))
        style.configure("Secondary.TButton", font=("Arial", 10))

        # Настройка иконок
        self.iconphoto(False, tk.PhotoImage(file=self.get_resource_path("icons/app_icon.png")))

    def create_menu(self):
        """Создание главного меню приложения."""
        menu_bar = tk.Menu(self)

        # Меню "Файл"
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Новая оценка", command=self.new_rating)
        file_menu.add_command(label="Открыть...", command=self.open_file)
        file_menu.add_command(label="Сохранить...", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.quit)
        menu_bar.add_cascade(label="Файл", menu=file_menu)

        # Меню "Правка"
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Настройки", command=self.show_settings)
        menu_bar.add_cascade(label="Правка", menu=edit_menu)

        # Меню "Инструменты"
        tools_menu = tk.Menu(menu_bar, tearoff=0)
        tools_menu.add_command(label="Анализ отзывов", command=self.analyze_reviews)
        menu_bar.add_cascade(label="Инструменты", menu=tools_menu)

        # Меню "Справка"
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Руководство пользователя", command=self.show_help)
        help_menu.add_command(label="О программе", command=self.show_about)
        menu_bar.add_cascade(label="Справка", menu=help_menu)

        self.config(menu=menu_bar)

    def show_results(self, category_ratings, criteria_ratings, total_rating, hotel_name=None):
        """Отображение результатов оценки."""
        self.rating_panel.pack_forget()
        self.result_panel.set_results(category_ratings, criteria_ratings, total_rating, hotel_name)
        self.result_panel.pack(fill=tk.BOTH, expand=True)

    def new_rating(self):
        """Начать новую оценку."""
        if hasattr(self, 'result_panel') and self.result_panel.winfo_ismapped():
            self.result_panel.pack_forget()
            self.rating_panel.pack(fill=tk.BOTH, expand=True)

        self.rating_panel.reset()
        self.notebook.select(0)  # Переключаемся на вкладку оценки

    def open_file(self):
        """Открыть файл с оценкой."""
        messagebox.showinfo("Информация", "Функция открытия файла будет доступна в следующей версии.")

    def save_file(self):
        """Сохранить оценку в файл."""
        messagebox.showinfo("Информация", "Функция сохранения в файл будет доступна в следующей версии.")

    def show_settings(self):
        """Показать настройки приложения."""
        messagebox.showinfo("Настройки", "Функция настроек будет доступна в следующей версии.")

    def search_hotel(self):
        """Поиск отеля."""
        messagebox.showinfo("Поиск отеля",
                            "Данная функция недоступна в текущей версии приложения.")

    def analyze_reviews(self):
        """Анализ отзывов."""
        messagebox.showinfo("Анализ отзывов",
                            "Эта функция позволит анализировать отзывы об отелях. " +
                            "Будет доступна в следующей версии.")

    def show_help(self):
        """Показать руководство пользователя."""
        help_text = """
        Руководство пользователя:

        1. Оценка отеля:
           - Выберите категорию для оценки (Обслуживание, Питание и т.д.)
           - Оцените каждый критерий по шкале от 0 до 10
           - Нажмите "Продолжить" для перехода к следующей категории
           - После оценки всех категорий введите название отеля
           - Нажмите "Сохранить отзыв" для сохранения результатов

        2. Просмотр отелей:
           - Перейдите на вкладку "Список отелей"
           - Выберите отель из списка для просмотра деталей
           - Используйте поиск для фильтрации списка

        3. API и парсер:
           - Используйте меню "Инструменты" -> "Поиск отеля"
           - Введите название отеля для поиска информации
           - Результаты будут отображены в новом окне
        """

        help_window = tk.Toplevel(self)
        help_window.title("Руководство пользователя")
        help_window.geometry("600x500")

        text = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text.insert(tk.END, help_text)
        text.config(state=tk.DISABLED)

        scrollbar = ttk.Scrollbar(help_window, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def show_about(self):
        """Показать информацию о программе."""
        about_text = """
        Система оценки отелей 2.0

        Разработана для выполнения:
        - Оценки отелей по детальным критериям
        - Расчета звездности отелей
        - Сохранения и анализа оценок
        - Интеграции с API гостиничных сервисов

        © 2025 Все права защищены
        """

        messagebox.showinfo("О программе", about_text)

    def get_resource_path(self, relative_path):
        """Получение пути к ресурсу."""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, "resources", relative_path)