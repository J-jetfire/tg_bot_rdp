import logging
import time

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.executor import start_polling
import subprocess
import sys

API_TOKEN = '7250780513:AAGG63paQPVpclx9AZK_Db0x3GQySHGJE4w'


# Устанавливаем кодировку по умолчанию
sys.stdout.reconfigure(encoding='utf-8')

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


def check_rdp_status():
    result = subprocess.run(['sc', 'query', 'TermService'], capture_output=True, text=True, encoding='cp1251')
    if "RUNNING" in result.stdout:
        return "RUNNING"
    elif "STOPPED" in result.stdout:
        return "STOPPED"
    else:
        return "UNKNOWN"


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Выключить RDP", "Включить RDP"]
    keyboard.add(*buttons)
    await message.answer("Выберите действие:", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Выключить RDP")
async def disable_rdp(message: types.Message):
    try:
        result = subprocess.run(['net', 'stop', 'TermService'], capture_output=True, text=True, encoding='cp1251')
        status = check_rdp_status()
        print(status)
        if status == "STOPPED":
            logger.info("RDP отключен")
            await message.answer("RDP отключен.")
        else:
            await message.answer(f"Не удалось отключить RDP. {result.stdout}")

    except Exception as e:
        logger.error(f'Error: {e}')
        await message.answer("Ошибка отключения RDP")


@dp.message_handler(lambda message: message.text == "Включить RDP")
async def enable_rdp(message: types.Message):
    try:
        result = subprocess.run(['net', 'start', 'TermService'], capture_output=True, text=True, encoding='cp1251')
        status = check_rdp_status()
        print(status)
        if status == "RUNNING":
            logger.info("RDP включен")
            await message.answer("RDP включен.")
        else:
            await message.answer(f"Не удалось включить RDP. {result.stdout}")

    except Exception as e:
        logger.error(f'Error: {e}')
        await message.answer("Ошибка включения RDP")


if __name__ == '__main__':
    try:
        start_polling(dp, skip_updates=True)
    except Exception as e:
        logger.error(f'Error starting polling: {e}')
    finally:
        while True:
            time.sleep(60)  # Блокируем выполнение, чтобы скрипт не завершался
