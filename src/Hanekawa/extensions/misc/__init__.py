from discord.ext.commands.bot import Bot

from .core import Misc


# Setup for when extension is loaded
async def setup(bot: Bot) -> None:
    cog = Misc(bot)
    await bot.add_cog(cog)
