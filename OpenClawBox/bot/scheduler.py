"""Background tasks for OpenClawBox bot."""

import asyncio
from aiogram import Bot
from database import get_user, get_usage_stats, reset_daily_usage


async def usage_warning_task(bot: Bot):
    """Send warning when user approaches limit."""
    while True:
        await asyncio.sleep(3600)  # Every hour
        
        # Get all users with high usage (>75%)
        from database import get_db
        with get_db() as conn:
            users = conn.execute(
                "SELECT telegram_id, daily_limit, used_today FROM users WHERE used_today > daily_limit * 0.75"
            ).fetchall()
        
        for user in users:
            pct = (user["used_today"] / user["daily_limit"]) * 100 if user["daily_limit"] > 0 else 0
            
            if pct > 90:
                await bot.send_message(
                    user["telegram_id"],
                    "⚠️ Критический лимит: вы использовали 90%+ токенов!\nСброс в полночь."
                )
            elif pct > 75:
                await bot.send_message(
                    user["telegram_id"],
                    "🔸 Осталось мало токенов (75%+). Подумайте о /tier upgrade"
                )


async def daily_reset_task():
    """Reset daily usage at midnight."""
    while True:
        now = asyncio.get_event_loop().time()
        # Calculate seconds until midnight
        import time
        tomorrow = time.time() + 86400
        midnight = tomorrow - (tomorrow % 86400)
        
        await asyncio.sleep(midnight - time.time())
        reset_daily_usage()
        await asyncio.sleep(1)  # Prevent double run