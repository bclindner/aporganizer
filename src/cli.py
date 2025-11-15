import argparse
import bot

parser = argparse.ArgumentParser(
    prog="APOrganizer",
    description="Discord bot for organizing APWorlds."
)

parser.add_argument("-d", "--dbfile", help="Database file to use.", default="aporganizer.db")
parser.add_argument("-g", "--guild", help="Guild to use.")


def run():
    args = parser.parse_args()
    config = bot.APOrganizerConfig.from_args(args)
    bot.run(config)
