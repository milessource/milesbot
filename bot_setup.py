from __future__ import annotations

from config import configuration

import disnake
from disnake.ext import commands

intents: disnake.Intents = disnake.Intents.all()
bot_instance: commands.Bot = commands.Bot(command_prefix='>', intents=intents, owner_ids=configuration.oids)

from os import listdir
for file in listdir("modules/"):
    if not file.endswith(".py"): continue
    bot_instance.load_extension(f"modules.{file[:-3]}")
