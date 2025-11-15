from typing import Self
import os
import tempfile
import argparse
from dataclasses import dataclass
from zipfile import ZipFile

import discord
from discord import app_commands

import aporganizer as apo

@dataclass
class APOrganizerConfig:
    intents: discord.Intents = discord.Intents.default()
    guild: str | None = None
    db_file: str = ":memory:"

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> Self:
        config = cls()
        if args.guild is not None:
            config.guild = args.guild
        if args.dbfile is not None:
            config.db_file = args.dbfile
        return config

class APOrganizerClient(discord.Client):

    user: discord.ClientUser

    def __init__(self, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.config = APOrganizerConfig()
        self.organizer = None # to be configured by setup_hook

    async def setup_hook(self):
        guild = None
        if self.config.guild is not None:
            guild = discord.Object(id=self.config.guild)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        self.organizer = apo.APOrganizer(self.config.db_file)

intents = discord.Intents.default()
client = APOrganizerClient(intents=intents)

@client.tree.command(description="Pings the server.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"{interaction.user.mention} Pong!")

@client.tree.command(description="Adds a YAML to the rando.")
@app_commands.describe(yaml="YAML file to add to the rando.")
async def addyaml(interaction: discord.Interaction, yaml: discord.Attachment):
    try:
        apo_yaml = client.organizer.add_yaml(str(interaction.user.id), await yaml.read())
        await interaction.response.send_message(
            f"YAML successfully added for slot \"{apo_yaml.slot_name}\"."
        )
    except apo.InvalidYamlException as e:
        await interaction.response.send_message(
            "Failed - YAML is not valid (either bad YAML or `name` was not set).",
            ephemeral=True
        )
    except apo.AlreadyExistsException as e:
        await interaction.response.send_message(f"Failed - {e}.", ephemeral=True)

@client.tree.command(description="Remove a YAML from the rando.")
@app_commands.describe(slot="Name of the slot to remove.")
async def removeyaml(interaction: discord.Interaction, slot: str):
    try:
        client.organizer.delete_yaml(slot)
        await interaction.response.send_message(
            f"YAML for {slot} successfully removed."
        )
    except apo.AlreadyExistsException as e:
        await interaction.response.send_message(
            f"Failed - could not find a YAML with the slot {slot}.",
            ephemeral=True
        )

@client.tree.command(description="Adds an APWorld to the rando.")
@app_commands.describe(game_name="Name of the game.", apworld="APWorld file to add to the rando.")
async def addapworld(interaction: discord.Interaction, game_name: str, apworld: discord.Attachment):
    try:
        client.organizer.add_apworld(
            str(interaction.user.id),
            game_name, await
            apworld.read()
        )
        await interaction.response.send_message(
            f"YAML successfully added for \"{game_name}\"."
        )
    except apo.AlreadyExistsException as e:
        await interaction.response.send_message(
            f"Failed - APWorld for {game_name} already exists." +
            "\nUse `/deleteapworld` to delete it if necessary.",
            ephemeral=True
        )

@client.tree.command(description="Exports all the rando files as a .zip, and clears the bot.")
async def export(interaction: discord.Interaction):
    # create temp zip file
    with tempfile.TemporaryFile() as temp_fd:
        with ZipFile(temp_fd, "w") as zip:
            # list APWorlds and save each by game name
            for apworld in client.organizer.get_apworlds():
                # TODO FIXME UNSAFE
                filename = "apworlds/" + apworld.game_name + ".apworld"
                with zip.open(filename, "w") as apworld_fd:
                    apworld_fd.write(apworld.data)
            for yaml in client.organizer.get_yamls():
                # TODO FIXME UNSAFE
                filename = "yamls/" + yaml.slot_name + ".yaml"
                with zip.open(filename, "w") as yaml_fd:
                    yaml_fd.write(yaml.data)
        # discord.py will try to read from wherever the current fd head is so
        # we need to flush/seek to 0
        temp_fd.flush()
        temp_fd.seek(0)
        client.organizer.clear()
        date = date.now()
        await interaction.response.send_message(
                "Exported and cleared. Enjoy your randomizer!",
                file=discord.File(temp_fd, "rando.zip")
        )

@client.tree.command(description="Describe all the YAMLs/APWorlds in the bot so far.")
async def status(interaction: discord.Interaction):
    response = ""
    # add yamls
    response += "**YAMLs:**"
    for yaml in client.organizer.get_yamls():
        user = await client.fetch_user(int(yaml.creator_id))
        response += f"\n* `{yaml.slot_name}` ({user.mention})"
    # add apworlds
    response += "\n**APWorlds:**"
    for apworld in client.organizer.get_apworlds():
        user = await client.fetch_user(int(apworld.creator_id))
        response += f"\n* `{apworld.game_name}` ({user.mention})"
    await interaction.response.send_message(response)

@client.tree.command(description="Clear the YAMLs and APWorlds from the bot (i.e. to start a new randomizer).")
async def clear(interaction: discord.Interaction):
    client.organizer.clear()
    await interaction.response.send_message("YAMLs and APWorlds cleared.")

def run(config):
    if "BOT_TOKEN" not in os.environ:
        raise Exception("No BOT_TOKEN environment variable set.")
    token = os.environ["BOT_TOKEN"]
    client.config = config
    client.run(token)
