# import asyncio
# from aiogram import Bot, Dispatcher, types
# from aiogram.filters import Command
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
# from PIL import Image, ImageDraw, ImageFont
# import os
#
# API_TOKEN = "8719060538:AAFMQyZAWGOHQuK2NLxmNdPp3Sl3HVZjKsU"
#
# bot = Bot(token=API_TOKEN)
# dp = Dispatcher()
#
# GAME_NAME = "⚡ VIOLET STORM"
# GAME_DESCRIPTION = (
#     "Добро пожаловать в мир сиреневого шторма!\n\n"
#     "🎮 Это нейро-игра, где ты сможешь:\n"
#     "• Проверить свою реакцию и ловкость\n"
#     "• Сразиться с искусственным интеллектом\n"
#     "• Открыть уникальные уровни\n"
#     "• Заработать достижения\n\n"
#     "Готова принять вызов? Жми на кнопку!"
# )
# GAME_URL = "https://твоя-ссылка-на-игру.com"
#
#
# def create_post_image():
#     width = 800
#     image_height = 450
#     text_height = 350
#     total_height = image_height + text_height
#
#     # Чёрный фон
#     img = Image.new('RGB', (width, total_height), '#000000')
#     draw = ImageDraw.Draw(img)
#
#     # Верхняя картинка
#     image_path = "game_image.jpg"
#     if os.path.exists(image_path):
#         top_img = Image.open(image_path)
#         top_img = top_img.resize((width, image_height), Image.Resampling.LANCZOS)
#         img.paste(top_img, (0, 0))
#     else:
#         # Фиолетовая заглушка
#         for y in range(image_height):
#             r = int(30 + (80 - 30) * y / image_height)
#             g = int(5 + (20 - 5) * y / image_height)
#             b = int(50 + (120 - 50) * y / image_height)
#             draw.line([(0, y), (width, y)], fill=(r, g, b))
#         try:
#             font = ImageFont.truetype("arial.ttf", 30)
#         except:
#             font = ImageFont.load_default()
#         draw.text((width // 2, image_height // 2), "🟣 ТВОЯ КАРТИНКА 🟣",
#                   fill='#a78bfa', font=font, anchor="mm")
#
#     # Плавный переход от картинки к чёрному
#     for y in range(40):
#         alpha = y / 40
#         r = int(80 * (1 - alpha) + 0)
#         g = int(20 * (1 - alpha) + 0)
#         b = int(120 * (1 - alpha) + 0)
#         draw.line([(0, image_height - 40 + y), (width, image_height - 40 + y)], fill=(r, g, b))
#
#     # Шрифты
#     try:
#         title_font = ImageFont.truetype("arial.ttf", 52)
#         desc_font = ImageFont.truetype("arial.ttf", 20)
#     except:
#         title_font = ImageFont.load_default()
#         desc_font = ImageFont.load_default()
#
#     y = image_height + 30
#
#     # Название игры (фиолетовое)
#     draw.text((50, y), GAME_NAME, fill='#a78bfa', font=title_font)
#
#     # Линия под названием (ярко-фиолетовая)
#     y += 65
#     draw.line([(50, y), (280, y)], fill='#7c3aed', width=3)
#
#     # Описание (светло-фиолетовый текст)
#     y += 30
#     lines = GAME_DESCRIPTION.split('\n')
#     for line in lines:
#         if line.strip():
#             # Заголовки и эмодзи — ярким фиолетовым
#             if '🎮' in line or '•' in line:
#                 draw.text((50, y), line, fill='#c4b5fd', font=desc_font)
#             else:
#                 draw.text((50, y), line, fill='#8b8b9e', font=desc_font)
#             y += 30
#         else:
#             y += 10
#
#     img.save("post.png", quality=95)
#     return "post.png"
#
#
# @dp.message(Command("start"))
# async def cmd_start(message: types.Message):
#     image_path = create_post_image()
#
#     # Кнопка с фиолетовой ссылкой
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="🎮 ИГРАТЬ", url=GAME_URL)]
#     ])
#
#     photo = FSInputFile(image_path)
#     await message.answer_photo(
#         photo=photo,
#         caption=f"<b>{GAME_NAME}</b>\n\n{GAME_DESCRIPTION}",
#         reply_markup=keyboard,
#         parse_mode="HTML"
#     )
#
#
# async def main():
#     print("Бот VIOLET STORM запущен!")
#     await dp.start_polling(bot)
#
#
# if __name__ == '__main__':
#     asyncio.run(main())


import webbrowser
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
html_path = os.path.join(base_dir, 'index.html')

# Для Windows путь нужно начинать с file:///
# Для Mac/Linux — с file://
file_url = f'file:///{html_path}'

print(f"Открываю: {file_url}")
webbrowser.open(file_url)


