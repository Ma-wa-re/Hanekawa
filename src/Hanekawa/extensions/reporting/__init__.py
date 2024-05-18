from discord.ext.commands.bot import Bot
from .core import Reporting


# Setup for when extension is loaded
async def setup(bot: Bot) -> None:
    cog = Reporting(bot)
    await bot.add_cog(cog)
