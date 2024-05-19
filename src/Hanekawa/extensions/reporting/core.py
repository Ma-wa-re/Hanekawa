import logging

import discord
from discord import app_commands
from discord.ext import commands
from Hanekawa.client import Bot

from .modals import FourmChannelView, MessageReport, UserReport

logger = logging.getLogger(__name__)

__all__ = ["Reporting"]


class Reporting(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.report_msg_ctx = app_commands.ContextMenu(name="Report Message", callback=self.report_message)
        self.report_user_ctx = app_commands.ContextMenu(name="Report User", callback=self.report_user)
        self.bot.tree.add_command(self.report_msg_ctx)
        self.bot.tree.add_command(self.report_user_ctx)

    @app_commands.command(description="Setup the channel for reporting (Must be fourm channel)")
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.checks.has_permissions(manage_messages=True)
    async def report_setup(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            content="Please select the fourm channel to use. Must have report and feedback tags",
            view=FourmChannelView(self.bot.settings_table),
            ephemeral=True,
        )

    @app_commands.guild_only()
    async def report_message(self, interaction: discord.Interaction, message: discord.Message):
        await interaction.response.send_modal(MessageReport(self.bot.settings_table, message))

    @app_commands.guild_only()
    async def report_user(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.send_modal(UserReport(self.bot.settings_table, user))
