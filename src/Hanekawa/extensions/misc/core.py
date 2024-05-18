import logging

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands.bot import Bot

logger = logging.getLogger(__name__)

__all__ = ["Misc"]


class Misc(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command(description="pong")
    async def ping(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Pong!")
