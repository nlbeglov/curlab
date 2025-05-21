class HotelRatingSystem:
    def __init__(self):
        # Весовые коэффициенты для основных категорий
        self.category_weights = {
            'service_quality': 0.25,
            'infrastructure': 0.20,
            'location': 0.15,
            'dining': 0.20,
            'room_comfort': 0.20
        }

        # Границы для звездности отеля
        self.star_boundaries = {
            1: (0, 3.5),
            2: (3.5, 5.5),
            3: (5.5, 7.5),
            4: (7.5, 9.0),
            5: (9.0, 10.1)
        }

    def get_linguistic_value(self, value):
        """Определяет лингвистическое значение для числового значения"""
        if value <= 3:
            return "poor"
        elif value <= 7:
            return "average"
        else:
            return "excellent"

    def compute_category_rating(self, criteria_ratings):
        """
        Вычисляет среднюю оценку для категории на основе оценок по критериям

        Args:
            criteria_ratings: список оценок по критериям [0-10]

        Returns:
            средняя оценка для категории [0-10]
        """
        if not criteria_ratings:
            return 0

        return sum(criteria_ratings) / len(criteria_ratings)

    def compute_weighted_average(self, category_ratings):
        """
        Вычисляет взвешенное среднее значение для всех категорий

        Args:
            category_ratings: словарь {category_name: rating_value}

        Returns:
            взвешенное среднее значение [0-10]
        """
        weighted_sum = 0
        total_weight = 0

        for category, rating in category_ratings.items():
            if category in self.category_weights:
                weight = self.category_weights[category]
                weighted_sum += rating * weight
                total_weight += weight

        if total_weight > 0:
            return weighted_sum / total_weight
        else:
            return 0

    def compute_star_rating(self, weighted_avg):
        """
        Определяет звездность отеля на основе взвешенного среднего

        Args:
            weighted_avg: взвешенное среднее значение [0-10]

        Returns:
            звездность отеля [1-5]
        """
        for star, (min_val, max_val) in self.star_boundaries.items():
            if min_val <= weighted_avg < max_val:
                return star

        # Если значение выходит за границы
        if weighted_avg < 0:
            return 1
        else:
            return 5

    def apply_rules(self, category_ratings):
        """
        Применяет набор правил для уточнения звездности отеля

        Args:
            category_ratings: словарь {category_name: rating_value}

        Returns:
            уточненная звездность отеля или None, если правила не применимы
        """
        # Получаем лингвистические значения для каждой категории
        linguistic_values = {}
        for category, rating in category_ratings.items():
            linguistic_values[category] = self.get_linguistic_value(rating)

        # Правило 1: Если все параметры низкого качества, то 1 звезда
        if all(value == "poor" for value in linguistic_values.values()):
            return 1

        # Правило 2: Если большинство параметров низкого качества, то 1 звезда
        poor_count = list(linguistic_values.values()).count("poor")
        if poor_count >= 3:  # Большинство из 5 категорий
            return 1

        # Правило 3: Если обслуживание и инфраструктура среднего качества, то минимум 2 звезды
        if (linguistic_values.get('service_quality') == "average" and
                linguistic_values.get('infrastructure') == "average"):
            weighted_avg = self.compute_weighted_average(category_ratings)
            base_rating = self.compute_star_rating(weighted_avg)
            return max(2, base_rating)

        # Правило 4: Если все параметры среднего качества, то 3 звезды
        if all(value == "average" for value in linguistic_values.values()):
            return 3

        # Правило 5: Если большинство параметров высокого качества, то минимум 4 звезды
        excellent_count = list(linguistic_values.values()).count("excellent")
        if excellent_count >= 3:  # Большинство из 5 категорий
            return 4

        # Правило 6: Если все параметры высокого качества, то 5 звезд
        if all(value == "excellent" for value in linguistic_values.values()):
            return 5

        # Если ни одно из правил не сработало
        return None

    def calculate_final_rating(self, category_ratings):
        """
        Вычисляет окончательную звездность отеля

        Args:
            category_ratings: словарь {category_name: rating_value}

        Returns:
            (star_rating, weighted_avg): кортеж с звездностью и взвешенным средним
        """
        # Вычисляем взвешенное среднее
        weighted_avg = self.compute_weighted_average(category_ratings)

        # Определяем базовую звездность
        base_rating = self.compute_star_rating(weighted_avg)

        # Применяем правила для уточнения звездности
        rule_rating = self.apply_rules(category_ratings)

        # Если сработало одно из правил, используем его результат
        if rule_rating is not None:
            return rule_rating, weighted_avg
        else:
            return base_rating, weighted_avg

    def generate_explanation(self, category_ratings, criteria_ratings, star_rating):
        """
        Генерирует пояснение для полученной звездности отеля

        Args:
            category_ratings: словарь {category_name: rating_value}
            criteria_ratings: словарь {category_name: {criteria_name: rating_value}}
            star_rating: итоговая звездность отеля

        Returns:
            текстовое пояснение
        """
        explanation = f"Результат анализа: {star_rating} звезд\n\n"
        explanation += "Обоснование:\n"

        # Список категорий с их русскими названиями
        category_names = {
            'service_quality': 'Качество обслуживания',
            'infrastructure': 'Инфраструктура и удобства',
            'location': 'Местоположение',
            'dining': 'Питание и кухня',
            'room_comfort': 'Комфорт номеров'
        }

        # Оценка по каждой категории
        for category, rating in category_ratings.items():
            if category in category_names:
                category_name = category_names[category]

                if rating <= 3:
                    quality = "Низкое"
                elif rating <= 7:
                    quality = "Среднее"
                else:
                    quality = "Высокое"

                explanation += f"✓ {category_name}: {quality} ({rating:.1f}/10)\n"

                # Добавляем детали по критериям, если они есть
                if category in criteria_ratings:
                    for criteria_name, criteria_value in criteria_ratings[category].items():
                        explanation += f"   • {criteria_name}: {criteria_value}/10\n"

        # Добавление рекомендаций для улучшения
        if star_rating < 5:
            explanation += "\nРекомендации для повышения класса отеля:\n"

            if category_ratings.get('service_quality', 0) < 8:
                explanation += "• Улучшить качество обслуживания: обучение персонала, сокращение времени ожидания\n"
            if category_ratings.get('infrastructure', 0) < 8:
                explanation += "• Расширить инфраструктуру: добавить бассейн, фитнес-центр, спа и другие услуги\n"
            if category_ratings.get('location', 0) < 8:
                explanation += "• Улучшить доступность транспорта или предлагать трансфер до ключевых локаций\n"
            if category_ratings.get('dining', 0) < 8:
                explanation += "• Повысить качество питания: расширить меню, привлечь лучших поваров\n"
            if category_ratings.get('room_comfort', 0) < 8:
                explanation += "• Обновить номера: улучшить качество кроватей, добавить современную технику\n"

        return explanation