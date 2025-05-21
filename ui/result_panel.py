import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import sys
from PIL import Image, ImageTk, ImageFilter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Добавляем родительскую директорию в путь поиска модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rating_system import HotelRatingSystem
from database import Database


class ResultPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.rating_system = HotelRatingSystem()
        self.db = Database()

        # Создаем переменные для хранения результатов
        self.category_ratings = {}
        self.criteria_ratings = {}
        self.total_rating = 0
        self.hotel_name = None

        # Флаг для отслеживания сохранения отзыва
        self.review_saved = False

        # Создаем интерфейс
        self.create_widgets()

    def create_widgets(self):
        """Создание виджетов панели результатов."""
        # Основной контейнер
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Верхняя часть - заголовок и общий результат
        self.header_frame = ttk.Frame(self.main_container)
        self.header_frame.pack(fill=tk.X, pady=(0, 10))

        self.title_label = ttk.Label(self.header_frame, text="Результаты оценки отеля",
                                     style="Title.TLabel")
        self.title_label.pack(pady=10)

        self.hotel_name_var = tk.StringVar()
        self.hotel_name_label = ttk.Label(self.header_frame,
                                          textvariable=self.hotel_name_var,
                                          font=("Arial", 14, "bold"))
        self.hotel_name_label.pack(pady=5)

        self.rating_frame = ttk.Frame(self.header_frame)
        self.rating_frame.pack(pady=10)

        self.rating_label = ttk.Label(self.rating_frame, text="Звездность отеля:",
                                      font=("Arial", 12))
        self.rating_label.pack(side=tk.LEFT, padx=5)

        self.stars_frame = ttk.Frame(self.rating_frame)
        self.stars_frame.pack(side=tk.LEFT)

        # Звезды будут добавлены при обновлении результатов
        self.star_labels = []

        # Центральная часть - детали оценки и график
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Разделяем на две колонки
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.columnconfigure(1, weight=1)

        # Левая колонка - детали оценки
        self.details_frame = ttk.LabelFrame(self.content_frame, text="Детали оценки")
        self.details_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # Текстовое поле для отображения пояснений
        self.explanation_text = tk.Text(self.details_frame, wrap=tk.WORD, width=40, height=20)
        self.explanation_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Добавляем полосу прокрутки
        explanation_scrollbar = ttk.Scrollbar(self.details_frame, command=self.explanation_text.yview)
        explanation_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.explanation_text.config(yscrollcommand=explanation_scrollbar.set)

        # Правая колонка - график
        self.chart_frame = ttk.LabelFrame(self.content_frame, text="Визуализация оценки")
        self.chart_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        # Создаем фигуру для графика
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Нижняя часть - кнопки
        self.buttons_frame = ttk.Frame(self.main_container)
        self.buttons_frame.pack(fill=tk.X, pady=10)

        self.save_button = ttk.Button(self.buttons_frame, text="Сохранить отзыв",
                                      command=self.save_review, style="Primary.TButton")
        self.save_button.pack(side=tk.RIGHT, padx=5)

        self.export_button = ttk.Button(self.buttons_frame, text="Экспорт в PDF",
                                        command=self.export_to_pdf)
        self.export_button.pack(side=tk.RIGHT, padx=5)

        self.new_button = ttk.Button(self.buttons_frame, text="Новая оценка",
                                     command=self.start_new_review)
        self.new_button.pack(side=tk.LEFT, padx=5)

    def set_results(self, category_ratings, criteria_ratings, total_rating, hotel_name=None):
        """Установка результатов оценки и обновление интерфейса."""
        self.category_ratings = category_ratings
        self.criteria_ratings = criteria_ratings
        self.total_rating = total_rating
        self.hotel_name = hotel_name or "Неизвестный отель"
        self.review_saved = False  # Сбрасываем флаг сохранения при получении новых результатов

        # Активируем кнопку сохранения
        self.save_button.state(["!disabled"])

        # Обновляем название отеля
        self.hotel_name_var.set(self.hotel_name)

        # Обновляем звезды
        for star_label in self.star_labels:
            star_label.destroy()

        self.star_labels = []
        star_count = int(total_rating)

        for i in range(5):
            if i < star_count:
                star_text = "★"  # Закрашенная звезда
                star_color = "#FFD700"  # Золотой цвет
            else:
                star_text = "☆"  # Пустая звезда
                star_color = "#C0C0C0"  # Серый цвет

            star_label = ttk.Label(self.stars_frame, text=star_text,
                                   font=("Arial", 24), foreground=star_color)
            star_label.pack(side=tk.LEFT)
            self.star_labels.append(star_label)

        # Обновляем пояснения
        self.explanation_text.config(state=tk.NORMAL)
        self.explanation_text.delete(1.0, tk.END)

        explanation = self.rating_system.generate_explanation(
            self.category_ratings, self.criteria_ratings, self.total_rating
        )

        self.explanation_text.insert(tk.END, explanation)
        self.explanation_text.config(state=tk.DISABLED)

        # Обновляем график
        self.update_chart()

    def update_chart(self):
        """Обновление графика с визуализацией данных."""
        self.ax.clear()

        # Категории и значения
        categories = [
            'Обслуживание', 'Инфраструктура',
            'Местоположение', 'Питание', 'Комфорт'
        ]

        values = [
            self.category_ratings.get('service_quality', 0),
            self.category_ratings.get('infrastructure', 0),
            self.category_ratings.get('location', 0),
            self.category_ratings.get('dining', 0),
            self.category_ratings.get('room_comfort', 0)
        ]

        # Создаем лепестковую диаграмму
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        values += values[:1]  # Замыкаем график
        angles += angles[:1]

        self.ax.fill(angles, values, color='skyblue', alpha=0.25)
        self.ax.plot(angles, values, 'o-', linewidth=2, color='blue')

        # Добавляем сетку и метки
        self.ax.set_xticks(angles[:-1])
        self.ax.set_xticklabels(categories)
        self.ax.set_yticks([1, 2, 3, 4, 5])  # Изменено для шкалы 0-5
        self.ax.set_yticklabels(['1', '2', '3', '4', '5'])  # Изменено для шкалы 0-5
        self.ax.set_ylim(0, 5)  # Изменено для шкалы 0-5

        # Заголовок
        self.ax.set_title(f'Звездность отеля: {self.total_rating}★', size=15)

        # Обновляем график
        self.canvas.draw()

    def save_review(self):
        """Сохранение отзыва в базу данных."""
        # Проверяем, был ли уже сохранен отзыв
        if self.review_saved:
            messagebox.showinfo("Информация", "Отзыв уже был сохранен в базу данных.")
            return

        if not self.hotel_name:
            new_name = simpledialog.askstring("Название отеля",
                                              "Введите название отеля:",
                                              parent=self)
            if not new_name:
                messagebox.showwarning("Предупреждение",
                                       "Необходимо указать название отеля для сохранения.")
                return

            self.hotel_name = new_name
            self.hotel_name_var.set(self.hotel_name)

        try:
            # Добавляем отель в базу данных
            hotel_id = self.db.add_hotel(self.hotel_name)

            # Получаем все критерии из базы данных
            criteria_data = self.db.get_rating_criteria()

            # Формируем словарь с ID критериев
            criteria_ids = {}
            for category in criteria_data:
                for criteria in category['criteria']:
                    criteria_key = f"{category['name']}_{criteria['name']}"
                    criteria_ids[criteria_key] = criteria['id']

            # Формируем данные для сохранения оценок по критериям
            criteria_ratings_db = {}
            for category_name, criteria_dict in self.criteria_ratings.items():
                for criteria_name, rating in criteria_dict.items():
                    criteria_key = f"{category_name}_{criteria_name}"
                    if criteria_key in criteria_ids:
                        criteria_ratings_db[criteria_ids[criteria_key]] = rating

            # Добавляем отзыв в базу данных
            weighted_avg = sum(self.category_ratings.values()) / len(self.category_ratings)
            review_id = self.db.add_review(
                hotel_id, self.total_rating, weighted_avg, criteria_ratings_db
            )

            messagebox.showinfo("Успешно",
                                f"Отзыв для отеля '{self.hotel_name}' успешно сохранен в базу данных.")

            # Отмечаем, что отзыв сохранен и блокируем кнопку
            self.review_saved = True
            self.save_button.state(["disabled"])

            # Обновляем список отелей в главном приложении
            if hasattr(self.parent.master, 'hotel_list_panel'):
                self.parent.master.hotel_list_panel.refresh_hotel_list()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить отзыв: {e}")

    def export_to_pdf(self):
        """Экспорт результатов в PDF."""
        try:
            import reportlab
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
            import tempfile
            import os
            from tkinter import filedialog

            # Спрашиваем, куда сохранить PDF
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Сохранить отчет как"
            )

            if not file_path:
                return

            # Сохраняем график во временный файл
            temp_dir = tempfile.gettempdir()
            chart_path = os.path.join(temp_dir, "hotel_chart.png")
            self.fig.savefig(chart_path, dpi=300, bbox_inches='tight')

            # Создаем PDF документ
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            styles = getSampleStyleSheet()

            # Добавляем собственный стиль для заголовка с другим именем
            custom_title_style = ParagraphStyle(name='CustomTitle',
                                                parent=styles['Heading1'],
                                                fontSize=16,
                                                spaceAfter=12)

            # Создаем содержимое документа
            content = []

            # Заголовок
            title = Paragraph(f"Отчет об оценке отеля: {self.hotel_name}", custom_title_style)
            content.append(title)
            content.append(Spacer(1, 12))

            # Общая оценка
            rating_text = f"Итоговая оценка: {self.total_rating} звезд из 5"
            rating_para = Paragraph(rating_text, styles['Heading2'])
            content.append(rating_para)
            content.append(Spacer(1, 12))

            # Добавляем график
            if os.path.exists(chart_path):
                img = Image(chart_path, width=400, height=300)
                content.append(img)
                content.append(Spacer(1, 12))

            # Детали оценки по категориям
            content.append(Paragraph("Детали оценки по категориям:", styles['Heading2']))
            content.append(Spacer(1, 6))

            # Таблица с результатами
            category_names = {
                'service_quality': 'Качество обслуживания',
                'infrastructure': 'Инфраструктура и удобства',
                'location': 'Местоположение',
                'dining': 'Питание и кухня',
                'room_comfort': 'Комфорт номеров'
            }

            data = [["Категория", "Оценка (из 10)"]]
            for category, rating in self.category_ratings.items():
                if category in category_names:
                    data.append([category_names[category], f"{rating:.1f}"])

            table = Table(data, colWidths=[300, 100])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            content.append(table)
            content.append(Spacer(1, 12))

            # Подробности по критериям
            content.append(Paragraph("Детали оценки по критериям:", styles['Heading2']))
            content.append(Spacer(1, 6))

            for category, criteria_dict in self.criteria_ratings.items():
                if category in category_names:
                    content.append(Paragraph(category_names[category], styles['Heading3']))
                    content.append(Spacer(1, 3))

                    criteria_data = [["Критерий", "Оценка (из 10)"]]
                    for criteria_name, rating in criteria_dict.items():
                        criteria_data.append([criteria_name, f"{rating}"])

                    criteria_table = Table(criteria_data, colWidths=[300, 100])
                    criteria_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))

                    content.append(criteria_table)
                    content.append(Spacer(1, 6))

            # Рекомендации
            if self.total_rating < 5:
                content.append(Paragraph("Рекомендации для повышения класса отеля:", styles['Heading2']))
                content.append(Spacer(1, 6))

                recommendations = []
                if self.category_ratings.get('service_quality', 0) < 8:
                    recommendations.append(
                        "• Улучшить качество обслуживания: обучение персонала, сокращение времени ожидания")
                if self.category_ratings.get('infrastructure', 0) < 8:
                    recommendations.append(
                        "• Расширить инфраструктуру: добавить бассейн, фитнес-центр, спа и другие услуги")
                if self.category_ratings.get('location', 0) < 8:
                    recommendations.append(
                        "• Улучшить доступность транспорта или предлагать трансфер до ключевых локаций")
                if self.category_ratings.get('dining', 0) < 8:
                    recommendations.append("• Повысить качество питания: расширить меню, привлечь лучших поваров")
                if self.category_ratings.get('room_comfort', 0) < 8:
                    recommendations.append(
                        "• Обновить номера: улучшить качество кроватей, добавить современную технику")

                for rec in recommendations:
                    content.append(Paragraph(rec, styles['Normal']))
                    content.append(Spacer(1, 3))

            # Дата создания отчета
            from datetime import datetime
            date_str = datetime.now().strftime("%d.%m.%Y %H:%M")
            content.append(Spacer(1, 20))
            content.append(Paragraph(f"Отчет создан: {date_str}", styles['Normal']))

            # Сохраняем PDF
            doc.build(content)

            # Предлагаем открыть файл
            if messagebox.askyesno("Экспорт завершен",
                                   f"Отчет успешно сохранен в {file_path}. Открыть файл?"):
                import subprocess
                import os
                import platform

                if platform.system() == 'Windows':
                    os.startfile(file_path)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.call(('open', file_path))
                else:  # Linux
                    subprocess.call(('xdg-open', file_path))

            # Удаляем временные файлы
            if os.path.exists(chart_path):
                os.remove(chart_path)

        except ImportError:
            messagebox.showwarning("Предупреждение",
                                   "Для экспорта в PDF требуется модуль reportlab. " +
                                   "Установите его с помощью команды: pip install reportlab")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать в PDF: {e}")

    def start_new_review(self):
        """Начало новой оценки."""
        # Поиск главного приложения в иерархии родителей
        app = self.parent
        while app and not hasattr(app, 'new_rating'):
            app = app.master

        if app and hasattr(app, 'new_rating'):
            app.new_rating()
        else:
            # Если не нашли главное приложение, попробуем напрямую обратиться к notebook
            try:
                notebook = self.parent.master.notebook
                rating_panel = self.parent.master.rating_panel

                # Скрываем панель результатов
                self.pack_forget()

                # Показываем панель оценки
                rating_panel.reset()
                rating_panel.pack(fill=tk.BOTH, expand=True)

                # Переключаемся на вкладку оценки
                notebook.select(0)
            except:
                messagebox.showerror("Ошибка", "Не удалось начать новую оценку.")