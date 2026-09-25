import json
import random
import logging
from telegram.ext import Application

# Enable logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

BOT_TOKEN = "8919624517:AAHZWaZafyXecaiQ9w0IXisDCVRB-jQw7JI"      # Paste your BotFather token
GROUP_CHAT_ID = "@jeecommunity1"  # Paste your group chat ID (e.g. -100123456789)

# Load questions from JSON
with open("questions.json", "r", encoding="utf-8") as f:
    JEE_QUESTIONS = json.load(f)

async def send_quiz_poll(context):
    q = random.choice(JEE_QUESTIONS)
    
    # Send quiz mode poll to group
    await context.bot.send_poll(
        chat_id=GROUP_CHAT_ID,
        question=q["question"][:300],  # Max 300 chars
        options=[opt[:100] for opt in q["options"]],  # Max 100 chars per option
        type="quiz",
        correct_option_id=int(q["correct_id"]),
        explanation=q.get("explanation", "")[:200],  # Max 200 chars
        is_anonymous=True
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Schedule poll every 1 hour (3600 seconds)
    # Change interval=3600 to whatever interval you want in seconds
    job_queue = app.job_queue
    job_queue.run_repeating(send_quiz_poll, interval=1800, first=10)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
