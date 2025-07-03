import json
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
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

... (same target text)
"""

def load_data():
    if os.path.exists(DATA_FILE):
        return json.load(open(DATA_FILE))
    return {"day": 1, "completed": {}}

def save_data(data):
    json.dump(data, open(DATA_FILE, "w"), indent=2)

progress = load_data()

def mark_task_done(task):
    d = str(progress["day"])
    progress["completed"].setdefault(d, {})[task] = True
    save_data(progress)

def get_status_text():
    st = progress["completed"].get(str(progress["day"]), {})
    lines = [f"📅 Day {progress['day']}/50 Status:"]
    for t in TASKS:
        lines.append(("✅" if st.get(t) else "❌") + " " + t.capitalize())
    return "\n".join(lines)

def get_weekly_report():
    lines = ["📊 Weekly Progress:"]
    today = progress["day"]
    for d in range(max(1, today-6), today+1):
        cnt = len(progress["completed"].get(str(d), {}))
        lines.append(f"Day {d}: {cnt}/5 tasks done")
    return "\n".join(lines)

def get_random_quote():
    qs = [
        "🪖 Pain is temporary...",
        "🔥 Train insane or remain the same.",
        # ...
    ]
    return random.choice(qs)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    await update.message.reply_text(
        f"Welcome back, Bhai!\nYou're on Day {progress['day']}/50.\nCommands: /report /weekly_report /target"
    )
    await send_daily(ctx)

async def report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(get_status_text())

async def weekly_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(get_weekly_report())

async def target(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(TARGET_TEXT)

async def button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.from_user.id != ADMIN_ID: return
    if q.data == "back":
        return await send_daily(ctx)
    mark_task_done(q.data)
    kb = [[InlineKeyboardButton("⬅️ Back", callback_data="back")]]
    await q.edit_message_text(get_status_text(), reply_markup=InlineKeyboardMarkup(kb))

async def send_daily(ctx: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton(t.capitalize(), callback_data=t)] for t in TASKS]
    await ctx.bot.send_message(
        ADMIN_ID,
        f"🔥 Day {progress['day']}/50 Checklist:\nTap buttons",
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def morning(ctx: ContextTypes.DEFAULT_TYPE):
    await ctx.bot.send_message(ADMIN_ID, f"🌅 Good Morning, Bhai!\n{get_random_quote()}")
    await send_daily(ctx)

async def evening(ctx: ContextTypes.DEFAULT_TYPE):
    await ctx.bot.send_message(ADMIN_ID, "🌇 Evening Reminder:\nDon't forget your routine!")

async def next_day(ctx: ContextTypes.DEFAULT_TYPE):
    if progress["day"] < 50:
        progress["day"] += 1; save_data(progress)
        await ctx.bot.send_message(ADMIN_ID, f"🕛 Day {progress['day']} started!")
        await send_daily(ctx)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("weekly_report", weekly_report))
    app.add_handler(CommandHandler("target", target))
    app.add_handler(CallbackQueryHandler(button))

    sched = AsyncIOScheduler()
    sched.add_job(morning, "cron", hour=4, minute=0, args=[app.bot])
    sched.add_job(evening, "cron", hour=18, minute=0, args=[app.bot])
    sched.add_job(next_day, "cron", hour=0, minute=0, args=[app.bot])
    sched.start()

    print("✅ ArmyGD Bot running on v21+")
    app.run_polling()

if __name__ == "__main__":
    main()
