from dotenv import load_dotenv
import os
from app.services.discordBot import NBABetBot

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

if __name__ == "__main__":
    try:
        bot = NBABetBot(TOKEN)
        bot.run()
    except Exception as e:
        print(f"Error starting bot: {str(e)}")