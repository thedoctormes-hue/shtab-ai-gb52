#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""МСК ГАСТРО ДАЙДЖЕСТ — v6.1 (Программный дисклеймер + sleep 2s)"""
import os, sys, json, asyncio, logging, random, re, hashlib
from datetime import datetime, timedelta, timezone
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv('/root/LabDoctorM/projects/telegram-bots/msk-gastro-digest-bot/.env')
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                    handlers=[logging.FileHandler("logs/digest.log", encoding="utf-8"), logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = "@moscovskiiest"  # Боевой канал (https://t.me/moscovskiiest)
AUTHOR_ID = os.getenv("AUTHOR_TELEGRAM_ID")
OR_KEY = os.getenv("OPENROUTER_API_KEY")
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
OR_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_PRICING = {
    "mistralai/mistral-small-creative": {"input": 0.1, "output": 0.3},
    "mistralai/mistral-nemo": {"input": 0.01, "output": 0.03},
    "x-ai/grok-3-mini": {"input": 0.3, "output": 0.5},
    "anthropic/claude-3-haiku": {"input": 0.25, "output": 1.25},
}
CH_FILE = "channels.json"
PROC_FILE = "processed.json"
DEFAULT_CHS = ["raidedrests", "restaurantmoscow", "vkusonomika", "sysoevfm", "thesaltmagazine", "michelinwontgive"]
VERDICTS = ["Хочу посетить", "Стоит проверить", "Есть сомнения", "Лучше пропустить"]
DISCLAIMER = "\n\n───\nДайджест сформирован при помощи AI. Хочешь также — напиши @doctormes"

VOICE_DNA = """Ты — главный редактор @moscovskiiest. Пишешь как для своих: честно, с лёгкой иронией, без глянца и пафоса.

СТРУКТУРА (строго соблюдай порядок и пустые строки между абзацами):
🍽️ МСК ГАСТРО | Дайджест
🗓 {date}
━━━━━━━━━━━━━━

[ХУК — ровно 4–7 слов. Цепляющий, без штампов.]

[АБЗАЦ 1] Главная новость или тренд дня. Объедини 2–3 факта из разных источников. Опиши атмосферу и контекст.

[АБЗАЦ 2] Вторая тема: закрытия, ребрендинги или скрытые инсайды. Контрастируй с первым абзацем. Сохрани живой ритм: длинное предложение → рубленое.

[АБЗАЦ 3] Планы, шефы, фестивали или нестандартные открытия. Погружай в детали концепции. Избегай списка! Пиши связным текстом.

[ВЕРДИКТ] — ровно одна строка из списка: {verdicts}

ЖЁСТКИЕ ПРАВИЛА:
• Форматирование: **жирный** для названий ресторанов и шефов, *курсив* для атмосферы и эмоций.
• Объём: 450–650 слов. Не обрывай мысль. Дай каждому абзацу воздух.
• Эмодзи обязательны (3–5 шт. на пост), только как точечные акценты (🍷🔥🥩🖤✨).
• СИНТЕЗИРУЙ информацию со ВСЕХ новостей ниже. Не пересказывай их по одной.
• Запрещено: списки, буллиты, выдуманный вкус/текстура, мат, «жажда крови» как маркер.
• Если новостей мало — углубляйся в контекст и атмосферу города.

ФАКТУРА ДЛЯ СИНТЕЗА:
{news}"""

def load_channels():
    if os.path.exists(CH_FILE):
        try:
            with open(CH_FILE, "r", encoding="utf-8") as f: data = json.load(f)
            if isinstance(data, list): return [c["handle"] if isinstance(c, dict) else c for c in data]
            return data.get("channels", DEFAULT_CHS) if isinstance(data, dict) else DEFAULT_CHS
        except: return DEFAULT_CHS
    return DEFAULT_CHS

def load_processed():
    if os.path.exists(PROC_FILE):
        try:
            with open(PROC_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def clean_hashes(data, hours=48):
    now = datetime.now().timestamp()
    return {h: t for h, t in data.items() if now - t < hours * 3600}

def html_sanitize(text):
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<i>\1</i>', text)
    text = text.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>').replace('&lt;i&gt;', '<i>').replace('&lt;/i&gt;', '</i>')
    return text

async def tg_send(chat_id, text, parse_mode="HTML"):
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(f"{TG_API}/sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode})
            return r.status_code == 200
    except Exception as e:
        logger.error(f"TG send error: {e}")
        return False

async def parse_channel(handle):
    url = f"https://t.me/s/{handle}"
    posts = []
    try:
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.get(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}); r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for msg in soup.select(".tgme_widget_message"):
            tm = msg.select_one("time"); tx = msg.select_one(".tgme_widget_message_text")
            if tm and tx and tm.has_attr("datetime"):
                dt = datetime.fromisoformat(tm["datetime"].replace("Z", "+00:00"))
                if dt > datetime.now(timezone.utc) - timedelta(hours=24):
                    t = " ".join(tx.get_text(strip=True).split())
                    if len(t) > 20 and not re.search(r"подпишись|скачай|реклама|промо", t, re.I):
                        posts.append({"text": t})
        return True, posts
    except Exception as e:
        logger.warning(f"Parse {handle} failed: {e}")
        return False, []

def score_and_dedup(raw_posts, processed):
    seen, unique = set(), []
    new_hashes = []  # Собираем хеши новых постов
    for p in raw_posts:
        h = hashlib.md5(p["text"].encode()).hexdigest()
        if h not in processed and p["text"] not in seen:
            seen.add(p["text"])
            t_l = p["text"].lower()
            score = 0
            if any(w in t_l for w in ["закры", "ушло", "скандал", "проверка"]): score += 2
            if any(w in t_l for w in ["откры", "запуск", "премьера", "дебют"]): score += 2
            if any(w in t_l for w in ["шеф", "мишлен", "звезда", "концепт"]): score += 2
            if len(p["text"]) > 100: score += 1
            p["score"] = score
            unique.append(p)
            new_hashes.append(h)  # Запоминаем хеш, но не добавляем в processed
    unique.sort(key=lambda x: x["score"], reverse=True)
    return unique[:10], new_hashes  # Возвращаем хеши отдельно

async def generate(news, date_str, model="mistralai/mistral-small-creative"):
    if not news: return None, 0, 0
    nt = "\n".join([f"• {n['text']}" for n in news])
    prompt = VOICE_DNA.format(date=date_str, verdicts=" | ".join(VERDICTS), news=nt)
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.75, "max_tokens": 3000}
    hdrs = {"Authorization": f"Bearer {OR_KEY}", "Content-Type": "application/json"}
    for _ in range(3):
        try:
            async with httpx.AsyncClient(timeout=180) as c:
                r = await c.post(OR_URL, json=payload, headers=hdrs); r.raise_for_status()
                resp = r.json()
                txt = resp["choices"][0]["message"]["content"].strip()
                usage = resp.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                if txt: return txt, prompt_tokens, completion_tokens
        except Exception as e:
            logger.warning(f"OR retry ({model}): {e}"); await asyncio.sleep(2)
    return None, 0, 0

def validate(text):
    clean = re.sub(r'<[^>]+>', '', text)
    banned = ["пиздец", "жажда крови"]
    if any(w in clean.lower() for w in banned): return False, "Запрещённые слова"
    if not any(v in clean for v in VERDICTS): return False, "Нет вердикта"
    lines = [l.strip() for l in clean.split('\n') if l.strip()]
    hook_line = ""
    for i, l in enumerate(lines):
        if "━" in l and i+1 < len(lines): hook_line = lines[i+1]; break
    if not hook_line and lines: hook_line = lines[0]
    words = hook_line.split()
    if len(words) < 4 or len(words) > 7: return False, f"Хук: {len(words)} слов"
    if len(lines) < 6: return False, "Пост слишком короткий"
    return True, "OK"

async def main():
    logger.info("=== Запуск v6.1 ===")
    chs = load_channels()
    processed = clean_hashes(load_processed())
    report = [f"📊 Отчёт за {datetime.now().strftime('%d.%m')}"]
    all_news = []
    
    # Парсинг с защитным sleep 2 секунды
    for h in chs:
        ok, posts = await parse_channel(h)
        report.append(f"{'✅' if ok else '❌'} @{h} → {len(posts)} постов")
        if ok: all_news.extend(posts)
        await asyncio.sleep(2)

    unique_news, new_hashes = score_and_dedup(all_news, processed)
    report.append(f"📦 Отобрано для синтеза: {len(unique_news)}")
    date_str = datetime.now().strftime("%d %B %Y")
    final_post = None

    # Цепочка моделей: основная → fallback 1 → fallback 2 → fallback 3
    MODELS = [
        "mistralai/mistral-small-creative",   # Основная (креативная)
        "mistralai/mistral-nemo",              # Fallback 1 (дешевая, 131k ctx)
        "x-ai/grok-3-mini",                   # Fallback 2 (стабильная, 131k ctx)
        "anthropic/claude-3-haiku",            # Fallback 3 (последний рубеж)
    ]

    # Рабочая копия новостей (будем уменьшать при сбоях)
    current_news = unique_news.copy()

    for model_idx, model in enumerate(MODELS):
        if not current_news:
            final_post = html_sanitize(f"🍽️ МСК ГАСТРО | Дайджест\n🗓 {date_str}\n━━━━━━━━━━━━━━\n\nТишина в ресторанной Москве. Воздух густой от ожиданий.")
            break

        logger.info(f"Попытка {model_idx+1}/{len(MODELS)}: {model}")
        report.append(f"🤖 Модель: {model.split('/')[-1]}")

        # 2 попытки валидации на каждую модель
        for attempt in range(2):
            digest, prompt_tokens, completion_tokens = await generate(current_news, date_str, model)
            # Рассчитываем стоимость генерации
            if digest and model in MODEL_PRICING:
                pricing = MODEL_PRICING[model]
                cost = (prompt_tokens * pricing["input"] + completion_tokens * pricing["output"]) / 1_000_000
                cost_msg = f"💸 Стоимость попытки {attempt+1}: ${cost:.6f} (модель {model.split('/')[-1]}, {prompt_tokens} in + {completion_tokens} out)"
                logger.info(cost_msg)
                report.append(cost_msg)
            if not digest:
                logger.warning(f"Модель {model} не вернула результат (попытка {attempt+1})")
                if attempt == 0:
                    await asyncio.sleep(3)  # Пауза перед повтором
                continue

            ok, reason = validate(digest)
            if ok:
                final_post = html_sanitize(digest)
                # Программное добавление дисклеймера (гарантия 100%)
                if DISCLAIMER.strip() not in final_post:
                    final_post += DISCLAIMER
                logger.info(f"✅ Успешно сгенерировано моделью {model}")
                break
            else:
                logger.warning(f"Валидация (модель {model}, попытка {attempt+1}): {reason}")

        if final_post:
            break  # Успешно сгенерировано, выходим из цикла моделей

        # Деградация контекста: уменьшаем количество новостей для следующей модели
        if len(current_news) > 3:
            new_count = max(3, len(current_news) // 2)
            logger.warning(f"Уменьшаем количество новостей: {len(current_news)} → {new_count}")
            current_news = current_news[:new_count]
            report.append(f"📉 Деградация: оставляем {new_count} новостей")
        else:
            logger.warning(f"Слишком мало новостей для деградации ({len(current_news)}), пробуем следующую модель")

    if not final_post:
        await tg_send(AUTHOR_ID, f"❌ Не пройдено после всех попыток\n" + "\n".join(report)); return

    if await tg_send(CHANNEL_ID, final_post):
        logger.info("✅ Опубликовано")
        # Только сейчас помечаем новости как обработанные
        for h in new_hashes:
            processed[h] = datetime.now().timestamp()
        with open(PROC_FILE, "w", encoding="utf-8") as f: json.dump(processed, f)
        await tg_send(AUTHOR_ID, "\n".join(report) + f"\n✅ v6.1 — Дайджест опубликован.")
    else: 
        await tg_send(AUTHOR_ID, "❌ Ошибка публикации\n" + "\n".join(report))

if __name__ == "__main__": asyncio.run(main())
