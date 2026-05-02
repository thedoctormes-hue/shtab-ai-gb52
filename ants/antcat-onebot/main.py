import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = "8649218949:AAESDIYZwLE-tHgC358jmnb9YEIBi3WNJ_A"
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я AntCatOnebot 🐜")

@dp.message()
async def echo(message: types.Message):
    await message.answer(f"Эхо: {message.text}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
