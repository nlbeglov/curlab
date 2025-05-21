import os
import sys

# Добавляем пути для импорта модулей
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from ui.app import HotelRatingApp

if __name__ == "__main__":
    # Создаем директорию для ресурсов, если ее нет
    resources_dir = os.path.join(current_dir, "resources")
    icons_dir = os.path.join(resources_dir, "icons")

    if not os.path.exists(resources_dir):
        os.makedirs(resources_dir)

    if not os.path.exists(icons_dir):
        os.makedirs(icons_dir)

    # Создаем иконку приложения, если ее нет
    app_icon_path = os.path.join(icons_dir, "app_icon.png")
    if not os.path.exists(app_icon_path):
        try:
            from PIL import Image, ImageDraw

            # Создаем простую иконку
            img = Image.new('RGB', (64, 64), color=(70, 130, 180))
            d = ImageDraw.Draw(img)

            # Рисуем символ отеля (здание)
            d.rectangle([16, 16, 48, 48], outline=(255, 255, 255), width=2)
            d.rectangle([24, 24, 32, 32], outline=(255, 255, 255), width=1)
            d.rectangle([36, 24, 44, 32], outline=(255, 255, 255), width=1)
            d.rectangle([24, 36, 32, 44], outline=(255, 255, 255), width=1)
            d.rectangle([36, 36, 44, 44], outline=(255, 255, 255), width=1)

            # Рисуем звезду
            d.polygon([32, 8, 36, 16, 44, 16, 38, 22, 40, 30, 32, 26, 24, 30, 26, 22, 20, 16, 28, 16],
                      fill=(255, 215, 0), outline=(255, 255, 255))

            # Сохраняем иконку
            img.save(app_icon_path)

        except ImportError:
            print("Не удалось создать иконку. Модуль PIL не установлен.")
        except Exception as e:
            print(f"Не удалось создать иконку: {e}")

    # Запускаем приложение
    app = HotelRatingApp()
    app.mainloop()