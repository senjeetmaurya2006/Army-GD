import asyncio
import json
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = "7777682673:AAE4kvErXvaUC0LmFD9WK_tvpoopUAO2x-4"
ADMIN_ID = 1972024725
DATA_FILE = "user_progress.json"
TASKS = ["run", "pushups", "pullups", "squats", "diet"]

TARGET_TEXT = """🏁 50 Days Army GD Target:

🗓️ Week 1–2:
- 1.5km Run in 8min
- 20 Pushups
- 10 Pullups
- 30 Squats
- Basic High Protein Diet

🗓️ Week 3–4:
- 2km Run in 8min
- 30 Pushups
- 12 Pullups
- 50 Squats
- Add core exercises (Plank, Crunches)

🗓️ Week 5–6:
- 2.5km Run in 7min
- 40 Pushups
- 14 Pullups
- 70 Squats
- Strict protein-rich diet

🗓️ Week 7–8:
- 3km Run in 6:30min
- 50 Pushups
- 16 Pullups
- 100 Squats
- Full day clean diet + sleep 7hr+ daily

🔥 Bonus (Last 6 Days):
- Mock Physical Test Daily
- Try 100 Pushups Challenge
- Mental Strength + Recovery Focus
"""

# Load or initialize data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"day": 1, "completed": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

progress = load_data()

def mark_task_done(task):
    day = str(progress["day"])
    if day not in progress["completed"]:
        progress["completed"][day] = {}
    progress["completed"][day][task] = True
    save_data(progress)

def get_status_text():
    status = progress.get("completed", {}).get(str(progress["day"]), {})
    lines = [f"📅 Day {progress['day']}/50 Status:"]
    for task in TASKS:
        done = "✅" if status.get(task) else "❌"
        lines.append(f"{done} {task.capitalize()}")
    return "\n".join(lines)

def get_weekly_report():
    report = ["📊 Weekly Progress:"]
    today = progress["day"]
    start = max(1, today - 6)
    for d in range(start, today + 1):
        status = progress.get("completed", {}).get(str(d), {})
        done_tasks = sum(1 for t in TASKS if status.get(t))
        report.append(f"Day {d}: {done_tasks}/5 tasks done")
    return "\n".join(report)

def get_random_quote():
    quotes = [
        "🪖 Pain is temporary, pride is forever.",
        "🔥 Train insane or remain the same.",
        "💪 Winners train, losers complain.",
        "🧠 Discipline is stronger than motivation.",
        "🇮🇳 You're not just building muscle, you're building character."
    ]
    return random.choice(quotes)

# Bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(
        f"Welcome back, Bhai!\nYou're on Day {progress['day']}/50.\nType /report, /weekly_report, or /target anytime!"
    )
    await send_daily_routine(context)

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(get_status_text())

async def weekly_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(get_weekly_report())

async def target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(TARGET_TEXT)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        return

    if query.data == "back":
        await send_daily_routine(context)
        return

    task = query.data
    mark_task_done(task)
    keyboard = [[InlineKeyboardButton("⬅️ Back to Checklist", callback_data="back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=get_status_text(), reply_markup=reply_markup)

async def send_daily_routine(context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(task.capitalize(), callback_data=task)] for task in TASKS]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🔥 Day {progress['day']}/50 Checklist:\nTap to mark done.",
        reply_markup=reply_markup
    )

async def send_morning_reminder(context: ContextTypes.DEFAULT_TYPE):
    quote = get_random_quote()
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"🌅 Good Morning, Bhai!\n{quote}")
    await send_daily_routine(context)

async def send_evening_reminder(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=ADMIN_ID, text="🌇 Evening Reminder:\nDon't forget to complete your routine!")

async def auto_next_day(context: ContextTypes.DEFAULT_TYPE):
    if progress["day"] < 50:
        progress["day"] += 1
        save_data(progress)
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"🕛 New Day Started: Day {progress['day']} ✅")
        await send_daily_routine(context)

# Run bot
async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("weekly_report", weekly_report))
    app.add_handler(CommandHandler("target", target))
    app.add_handler(CallbackQueryHandler(button_handler))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_morning_reminder, "cron", hour=4, minute=0, args=[app])
    scheduler.add_job(send_evening_reminder, "cron", hour=18, minute=0, args=[app])
    scheduler.add_job(auto_next_day, "cron", hour=0, minute=0, args=[app])
    scheduler.start()

    print("✅ ArmyGD Bot is running on Render...")
    await app.run_polling()

asyncio.run(run_bot())
