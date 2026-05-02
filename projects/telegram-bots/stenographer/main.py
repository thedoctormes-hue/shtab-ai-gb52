import asyncio, logging, os, sys, atexit, signal
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from core import config
from bot import handlers

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

PID_FILE = "/tmp/stenographerobot.pid"

def ensure_single_instance():
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE) as f: old_pid = int(f.read().strip())
            # Проверяем, что это наш процесс (PID не переиспользован)
            try:
                import psutil
                if psutil.pid_exists(old_pid) and psutil.Process(old_pid).cmdline() and "stenographer" in " ".join(psutil.Process(old_pid).cmdline()):
                    os.kill(old_pid, signal.SIGTERM)
                    logging.info(f"🛑 Остановлен дубль (PID {old_pid})")
            except (ImportError, psutil.NoSuchProcess, psutil.AccessDenied):
                # Без psutil — проверяем базовый способом
                try:
                    os.kill(old_pid, 0)  # Проверка существования процесса
                    os.kill(old_pid, signal.SIGTERM)
                    logging.info(f"🛑 Остановлен дубль (PID {old_pid})")
                except (ProcessLookupError, PermissionError): pass
        except (ValueError, PermissionError): pass
        finally:
            try: os.remove(PID_FILE)
            except: pass
    with open(PID_FILE, "w") as f: f.write(str(os.getpid()))
    atexit.register(lambda: os.path.exists(PID_FILE) and os.remove(PID_FILE))

async def main():
    ensure_single_instance()
    if not config.validate_config(): return
    bot = Bot(token=config.BOT_TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(handlers.router)
    me = await bot.get_me()
    logging.info(f"🟢 @{me.username} запущен (PID {os.getpid()})")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: logging.info("🛑 Ручной стоп")
    except Exception as e: logging.error(f"💥 Крит: {e}", exc_info=True)
