import os
import json
import random
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import Application, MessageHandler, PollAnswerHandler, ContextTypes, filters


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TARGET_CHAT_ID = "@jeecommunity1"

ADMIN_CHAT_ID = -3973293437

QUESTION_INTERVAL = 1800

reply_tracker = {}

user_stats = {}

# List of Appreciation Messages
APPRECIATION_MESSAGES = [
    "🏆 Outstanding, {name}! 3 correct in a row! You're unstoppable! 🔥",
    "🧠 Look at the big brain on {name}! 3 in a row, excellent job! 🎉",
    "🎯 Pure precision, {name}! 3 consecutive right answers! Keep rolling! 🚀",
    "⚡ {name} is on fire! 3 out of 3 right! Top tier performance! 👑"
    "🎓 AIR 1 in the making! {name} just nailed 3 questions straight! 🌟",
    "🔬 Textbook perfect execution, {name}! 3 in a row—physics and math bow to you! 📐",
    "💣 BOOM! 3 out of 3! {name} is absolute main-character energy right now! 💥",
    "🚀 Unstoppable momentum, {name}! That's 3 consecutive correct answers! Keep it up! 🏁",
    "🧠 Absolute genius at work! {name} just cleared 3 questions without breaking a sweat! 🧪",
    "🥇 High-level accuracy, {name}! 3 straight hits! You're making JEE look easy! 🎯"
    "👑 Absolute legend! {name} just effortlessly dropped a 3-peat of correct answers! ⚡",
    "🎯 Precision 100! {name} is putting on a masterclass right now with 3 in a row! 💯",
    "🚀 Stand back! {name} is on a streak that's sending them straight to IIT Bombay CSE! 🏰",
    "🧪 Pure brilliance, {name}! 3 straight hits without even needing a rough sheet! 📐",
    "🔥 {name} is cooking! 3 consecutive correct answers—the competition is sweating now! 💦",
    "🌟 Effortless execution! {name} is making these JEE-level questions look like primary school math! 🎓",
    "⚡ Unstoppable force! {name} just cleared 3 in a row! Give this person a medal already! 🥇",
    "🧠 High-IQ gameplay from {name}! 3 out of 3 right—absolute top-percentile energy! 📈",
    "💥 BOOM! 3 straight bullseyes from {name}! The hard work is clearly paying off! 📚",
    "🏆 Flawless performance, {name}! 3 consecutive answers locked in correctly! Keep dominating! 🔱"
]

# Savage JEE/NEET Exam Roasts
ROAST_MESSAGES = [
    "💀 {name}, negative marking exists just because of people like you. Drop the phone and open NCERT! 📖",
    "🤡 Bro {name}, even a random number generator would score higher than you. What was that attempt?! 🎲",
    "📉 {name} just single-handedly lowered the cutoff for everyone else in this group. Thank you for your service! 🫡",
    "🧠 {name}, did you select that option with your eyes closed or are you actively trying to get a 7-digit rank? 🎯",
    "🛑 Pause for a moment, {name}. Think about your dream college, then realize you won't get anywhere near it with answers like that! 🏫",
    "💨 {name}'s preparation level: 0%. Confidence level: 100%. Result: Pure disaster! 📉",
    "❌ {name}, if incorrect answers were JEE Advanced ranks, you'd be AIR 1 today! 🏆",
    "📚 {name}, please re-evaluate your life choices. That answer was an insult to basic physics and math! 🤦‍♂️",
    "🧟 {name} clicked that so fast without thinking... even the bot felt second-hand embarrassment! 🤖",
    "💸 {name}, your parents are paying tuition fees just for you to guess these options? 😭"
    "📉 {name}, even Newton's third law couldn't equal the force of how hard you just fell on that question! 🍎",
    "🤡 Bro {name}, did you pick that option based on your birth date or astrological sign? Because it sure wasn't logic! 🔮",
    "💀 {name}, you're making NTA look merciful right now. Please re-read the basics before clicking anything else! 🛑",
    "🤦‍♂️ {name} just proved that speed and accuracy are two completely different things! Slow down and actually read! 🐢",
    "🗑️ That answer from {name} was so far off, even the process of elimination couldn't save it! 🕯️",
    "📉 {name}'s percentile just hit absolute zero faster than liquid helium! 🧊",
    "🎪 Ladies and gentlemen, {name} is here to demonstrate what NOT to do in the exam hall! 👏",
    "📚 {name}, even a blank OMR sheet would have scored more relative points than that choice! 📝",
    "⚡ {name} clicked an answer so wrong that basic thermodynamics broke down trying to explain it! ⚛️",
    "🛑 Pause, {name}! Before you attempt the next one, promise us you'll open a textbook first! 📖"
]



async def send_automatic_questions(application: Application):
    await asyncio.sleep(5)
    while True:
        try:
            if os.path.exists("questions.json"):
                with open("questions.json", "r", encoding="utf-8") as f:
                    questions = json.load(f)
                
                if questions:
                    q = random.choice(questions)
                    
                    # Fallback lookup if key key varies
                    correct_id = q.get("correct_option_id") if "correct_option_id" in q else q.get("correct_option", 0)
                    
                    poll_message = await application.bot.send_poll(
                        chat_id=TARGET_CHAT_ID,
                        question=q["question"],
                        options=q["options"],
                        type="quiz",
                        correct_option_id=correct_id,
                        is_anonymous=False
                    )
                    
                    application.bot_data[poll_message.poll.id] = correct_id
                    print(f"[SUCCESS] Posted poll: {q['question']}")
            else:
                print("[ERROR] questions.json file not found.")
        except Exception as e:
            print(f"[ERROR] Failed to post question: {e}")
            
        await asyncio.sleep(QUESTION_INTERVAL)

async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.poll_answer
    user = answer.user
    user_id = user.id
    
    name = f"@{user.username}" if user.username else user.first_name

    if user_id not in user_stats:
        user_stats[user_id] = {"name": name, "streak": 0}

    poll_id = answer.poll_id
    correct_option_id = context.bot_data.get(poll_id)

    if answer.option_ids and answer.option_ids[0] == correct_option_id:
        user_stats[user_id]["streak"] += 1
        if user_stats[user_id]["streak"] == 3:
            msg = random.choice(APPRECIATION_MESSAGES).format(name=name)
            await context.bot.send_message(chat_id=TARGET_CHAT_ID, text=msg)
            user_stats[user_id]["streak"] = 0
    else:
        user_stats[user_id]["streak"] = 0
        roast_text = random.choice(ROAST_MESSAGES).format(name=name)
        await context.bot.send_message(chat_id=TARGET_CHAT_ID, text=roast_text)

# --- DUMMY HTTP SERVER TO KEEP RENDER FREE TIER ALIVE ---
async def handle_health_check(request):
    return web.Response(text="Bot is alive!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


async def handle_incoming_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Forward the incoming private message to the Admin Chat
    forwarded_msg = await context.bot.forward_message(
        chat_id=ADMIN_CHAT_ID,
        from_chat_id=user_id,
        message_id=update.message.message_id
    )
    
    # Map the forwarded message ID to the user ID for admin reply routing
    reply_tracker[forwarded_msg.message_id] = user_id
    await update.message.reply_text("Message received. An admin will get back to you shortly.")


async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the message is coming from the Admin Chat and is a reply to a forwarded message
    if update.effective_chat.id == ADMIN_CHAT_ID and update.message.reply_to_message:
        replied_msg_id = update.message.reply_to_message.message_id

        # Look up original sender ID from RAM tracker
        target_user_id = reply_tracker.get(replied_msg_id)

        if target_user_id:
            try:
                # Send message to user directly as the Bot
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=update.message.text
                )
                await update.message.reply_text("✅ Reply sent anonymously via Bot!")
            except Exception as e:
                await update.message.reply_text(f"❌ Failed to deliver message: {e}")

async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the message is coming from the Admin Chat and is a reply to a forwarded message
    if update.effective_chat.id == ADMIN_CHAT_ID and update.message.reply_to_message:
        replied_msg_id = update.message.reply_to_message.message_id

        # Look up original sender ID from RAM tracker
        target_user_id = reply_tracker.get(replied_msg_id)

        if target_user_id:
            try:
                # Send message to user directly as the Bot
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=update.message.text
                )
                await update.message.reply_text("✅ Reply sent anonymously via Bot!")
            except Exception as e:
                await update.message.reply_text(f"❌ Failed to deliver message: {e}")



async def main():
    await start_web_server()
    
    application = Application.builder().token(TOKEN).build()
    
    # 1. Existing quiz poll handler
    application.add_handler(PollAnswerHandler(handle_poll_answer))
    
    # 2. ADD THE NEW HANDLERS HERE:
    # Handle user messages in private chat
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, handle_incoming_user_message)
    )
    
    # Handle admin replies in the admin group/chat
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND & filters.REPLY, handle_admin_reply)
    )

    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        # Start automated quiz poster in background loop
        asyncio.create_task(send_automatic_questions(application))
        
        print("Bot is live, polling, and auto-posting questions...")
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
