import sqlite3
import os
from datetime import datetime


class Database:
    """Класс для работы с базой данных SQLite."""

    def __init__(self, db_name="hotel_ratings.db"):
        """Инициализация базы данных."""
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.create_tables()

    def connect(self):
        """Подключение к базе данных."""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self.conn, self.cursor

    def close(self):
        """Закрытие соединения с базой данных."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def create_tables(self):
        """Создание необходимых таблиц в базе данных."""
        conn, cursor = self.connect()

        # Таблица отелей
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS hotels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Таблица отзывов
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hotel_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            weighted_avg REAL NOT NULL,
            review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hotel_id) REFERENCES hotels (id)
        )
        ''')

        # Таблица категорий оценки
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS rating_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
        ''')

        # Таблица критериев оценки
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS rating_criteria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (category_id) REFERENCES rating_categories (id)
        )
        ''')

        # Таблица оценок по критериям
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS criteria_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_id INTEGER NOT NULL,
            criteria_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            FOREIGN KEY (review_id) REFERENCES reviews (id),
            FOREIGN KEY (criteria_id) REFERENCES rating_criteria (id)
        )
        ''')

        # Таблица для хранения изображений отелей
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS hotel_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hotel_id INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            is_main BOOLEAN DEFAULT 0,
            FOREIGN KEY (hotel_id) REFERENCES hotels (id)
        )
        ''')

        # Наполняем таблицу категорий, если она пустая
        cursor.execute("SELECT COUNT(*) FROM rating_categories")
        count = cursor.fetchone()[0]

        if count == 0:
            categories = [
                ("service_quality", "Качество обслуживания"),
                ("infrastructure", "Инфраструктура и удобства"),
                ("location", "Местоположение"),
                ("dining", "Питание и кухня"),
                ("room_comfort", "Комфорт номеров")
            ]

            cursor.executemany(
                "INSERT INTO rating_categories (name, description) VALUES (?, ?)",
                categories
            )

            # Получаем id добавленных категорий
            category_ids = {}
            for category_name, _ in categories:
                cursor.execute(
                    "SELECT id FROM rating_categories WHERE name = ?",
                    (category_name,)
                )
                category_ids[category_name] = cursor.fetchone()[0]

            # Критерии для "Качество обслуживания"
            service_criteria = [
                (category_ids["service_quality"], "Скорость регистрации", "0 - очень долго, 5 - очень быстро"),
                (category_ids["service_quality"], "Вежливость персонала", "0 - грубый, 5 - очень вежливый"),
                (category_ids["service_quality"], "Знание иностранных языков",
                 "0 - не знают, 5 - знают несколько языков"),
                (category_ids["service_quality"], "Готовность помочь", "0 - игнорируют, 5 - всегда готовы помочь"),
                (category_ids["service_quality"], "Профессионализм",
                 "0 - непрофессионально, 5 - высокий профессионализм")
            ]

            # Критерии для "Инфраструктура и удобства"
            infra_criteria = [
                (category_ids["infrastructure"], "Наличие бассейна",
                 "0 - нет, 3 - есть внутренний, 5 - есть внешний и внутренний"),
                (category_ids["infrastructure"], "Фитнес-центр", "0 - нет, 3 - минимальный, 5 - полноценный"),
                (category_ids["infrastructure"], "Спа-услуги", "0 - нет, 5 - широкий выбор"),
                (category_ids["infrastructure"], "Бизнес-центр", "0 - нет, 5 - полностью оборудованный"),
                (category_ids["infrastructure"], "Зоны отдыха", "0 - отсутствуют, 5 - множество комфортных зон"),
                (category_ids["infrastructure"], "Детские площадки", "0 - нет, 5 - есть с аниматорами")
            ]

            # Критерии для "Местоположение"
            location_criteria = [
                (category_ids["location"], "Близость к центру города", "0 - очень далеко, 5 - в центре"),
                (category_ids["location"], "Транспортная доступность", "0 - плохая, 5 - отличная"),
                (category_ids["location"], "Близость к достопримечательностям", "0 - далеко, 5 - рядом"),
                (category_ids["location"], "Тишина и спокойствие", "0 - шумно, 5 - тихо"),
                (category_ids["location"], "Безопасность района", "0 - опасно, 5 - безопасно")
            ]

            # Критерии для "Питание и кухня"
            dining_criteria = [
                (category_ids["dining"], "Чистота", "0 - грязно, 5 - идеально чисто"),
                (category_ids["dining"], "Подача блюд", "0 - некрасивая, 5 - шедевральная"),
                (category_ids["dining"], "Скорость подачи", "0 - долго, 5 - быстро"),
                (category_ids["dining"], "Вкус блюд", "0 - невкусно, 5 - очень вкусно"),
                (category_ids["dining"], "Разнообразие меню", "0 - ограниченное, 5 - широкий выбор"),
                (category_ids["dining"], "Учет пищевых предпочтений", "0 - не учитывают, 5 - полностью учитывают")
            ]

            # Критерии для "Комфорт номеров"
            room_criteria = [
                (category_ids["room_comfort"], "Чистота", "0 - грязно, 5 - идеально чисто"),
                (category_ids["room_comfort"], "Качество кровати", "0 - неудобная, 5 - очень комфортная"),
                (category_ids["room_comfort"], "Размер номера", "0 - тесно, 5 - просторно"),
                (category_ids["room_comfort"], "Шумоизоляция", "0 - плохая, 5 - отличная"),
                (category_ids["room_comfort"], "Состояние мебели", "0 - ветхая, 5 - новая"),
                (category_ids["room_comfort"], "Оснащение техникой", "0 - минимум, 5 - современная техника"),
                (category_ids["room_comfort"], "Качество интернета", "0 - нет или медленный, 5 - быстрый"),
                (category_ids["room_comfort"], "Вид из окна", "0 - неприятный, 5 - прекрасный"),
                (category_ids["room_comfort"], "Кондиционирование", "0 - отсутствует, 5 - работает идеально"),
                (category_ids["room_comfort"], "Ванная комната", "0 - минимальное оснащение, 5 - роскошная")
            ]

            # Объединяем все критерии
            all_criteria = service_criteria + infra_criteria + location_criteria + dining_criteria + room_criteria

            # Вставляем все критерии в таблицу
            cursor.executemany(
                "INSERT INTO rating_criteria (category_id, name, description) VALUES (?, ?, ?)",
                all_criteria
            )

        self.conn.commit()
        self.close()

    def add_hotel(self, name, address=""):
        """Добавление нового отеля в базу данных."""
        conn, cursor = self.connect()

        # Проверяем, существует ли уже отель с таким названием
        cursor.execute("SELECT id FROM hotels WHERE name = ?", (name,))
        existing_hotel = cursor.fetchone()

        if existing_hotel:
            hotel_id = existing_hotel[0]
        else:
            cursor.execute(
                "INSERT INTO hotels (name, address) VALUES (?, ?)",
                (name, address)
            )
            self.conn.commit()
            hotel_id = cursor.lastrowid

        self.close()
        return hotel_id

    def add_review(self, hotel_id, rating, weighted_avg, criteria_ratings):
        """
        Добавление нового отзыва в базу данных.

        Args:
            hotel_id: ID отеля
            rating: звездность отеля (от 1 до 5)
            weighted_avg: взвешенное среднее значение всех параметров
            criteria_ratings: словарь {criteria_id: rating_value}
        """
        conn, cursor = self.connect()

        # Добавляем отзыв
        cursor.execute(
            "INSERT INTO reviews (hotel_id, rating, weighted_avg) VALUES (?, ?, ?)",
            (hotel_id, rating, weighted_avg)
        )

        review_id = cursor.lastrowid

        # Добавляем оценки по критериям
        for criteria_id, rating_value in criteria_ratings.items():
            cursor.execute(
                "INSERT INTO criteria_ratings (review_id, criteria_id, rating) VALUES (?, ?, ?)",
                (review_id, criteria_id, rating_value)
            )

        self.conn.commit()
        self.close()
        return review_id

    def get_hotels(self):
        """Получение списка всех отелей."""
        conn, cursor = self.connect()

        cursor.execute("""
            SELECT h.id, h.name, h.address, COUNT(r.id) as review_count, 
                   ROUND(AVG(r.rating), 1) as avg_rating
            FROM hotels h
            LEFT JOIN reviews r ON h.id = r.hotel_id
            GROUP BY h.id
            ORDER BY h.name
        """)

        hotels = cursor.fetchall()
        self.close()
        return hotels

    def get_hotel_details(self, hotel_id):
        """Получение детальной информации об отеле."""
        conn, cursor = self.connect()

        # Получаем информацию об отеле
        cursor.execute("""
            SELECT h.id, h.name, h.address, COUNT(r.id) as review_count, 
                   ROUND(AVG(r.rating), 1) as avg_rating
            FROM hotels h
            LEFT JOIN reviews r ON h.id = r.hotel_id
            WHERE h.id = ?
            GROUP BY h.id
        """, (hotel_id,))

        hotel = cursor.fetchone()

        # Получаем все отзывы для этого отеля
        cursor.execute("""
            SELECT id, rating, weighted_avg, review_date
            FROM reviews
            WHERE hotel_id = ?
            ORDER BY review_date DESC
        """, (hotel_id,))

        reviews = cursor.fetchall()

        # Получаем оценки по критериям для каждого отзыва
        review_details = []
        for review in reviews:
            review_id = review[0]

            cursor.execute("""
                SELECT rc.name, cr.rating, rc.description, cat.name as category_name
                FROM criteria_ratings cr
                JOIN rating_criteria rc ON cr.criteria_id = rc.id
                JOIN rating_categories cat ON rc.category_id = cat.id
                WHERE cr.review_id = ?
                ORDER BY cat.id, rc.id
            """, (review_id,))

            criteria_ratings = cursor.fetchall()

            review_details.append({
                'review': review,
                'criteria_ratings': criteria_ratings
            })

        self.close()
        return hotel, review_details

    def get_rating_criteria(self):
        """Получение всех критериев оценки, сгруппированных по категориям."""
        conn, cursor = self.connect()

        cursor.execute("""
            SELECT c.id as category_id, c.name as category_name, c.description as category_desc,
                   r.id as criteria_id, r.name as criteria_name, r.description as criteria_desc
            FROM rating_categories c
            JOIN rating_criteria r ON c.id = r.category_id
            ORDER BY c.id, r.id
        """)

        rows = cursor.fetchall()

        # Формируем структуру "категория -> критерии"
        categories = {}
        for row in rows:
            category_id = row[0]

            if category_id not in categories:
                categories[category_id] = {
                    'id': category_id,
                    'name': row[1],
                    'description': row[2],
                    'criteria': []
                }

            categories[category_id]['criteria'].append({
                'id': row[3],
                'name': row[4],
                'description': row[5]
            })

        self.close()
        return list(categories.values())

    def add_hotel_image(self, hotel_id, image_path, is_main=False):
        """Добавление изображения отеля."""
        conn, cursor = self.connect()

        # Если это главное изображение, убираем флаг у других изображений
        if is_main:
            cursor.execute(
                "UPDATE hotel_images SET is_main = 0 WHERE hotel_id = ?",
                (hotel_id,)
            )

        cursor.execute(
            "INSERT INTO hotel_images (hotel_id, image_path, is_main) VALUES (?, ?, ?)",
            (hotel_id, image_path, is_main)
        )

        self.conn.commit()
        self.close()
        return cursor.lastrowid

    def get_hotel_images(self, hotel_id):
        """Получение всех изображений отеля."""
        conn, cursor = self.connect()

        cursor.execute(
            "SELECT id, image_path, is_main FROM hotel_images WHERE hotel_id = ? ORDER BY is_main DESC",
            (hotel_id,)
        )

        images = cursor.fetchall()
        self.close()
        return images