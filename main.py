import bot
import os

if __name__ == "__main__":
    if "BOT_TOKEN" not in os.environ:
        raise Exception("No BOT_TOKEN environment variable set.")
    bot.run(os.environ["BOT_TOKEN"])
