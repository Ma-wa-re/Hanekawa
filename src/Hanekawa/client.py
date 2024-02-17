import logging
import sys
from datetime import datetime, timedelta

import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional

from .config import Config

logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    __slots__ = (
        "config",
        "start_time",
    )

    def __init__(self, config: Config):
        self.config: Config = config
        self.start_time: datetime = datetime.utcnow()
        self.db_client: AsyncIOMotorClient = AsyncIOMotorClient(self.config.database_url)
        self.db: Optional[AsyncIOMotorDatabase]

        super().__init__(
            command_prefix=commands.when_mentioned,
            description="Hanekawa - To fill out later",
            intents=discord.Intents.default(),
            help_command=None,
        )

    @property
    def uptime(self) -> timedelta:
        """Gets bot's uptime"""

        return datetime.utcnow() - self.start_time

    def run_with_token(self) -> None:
        """Runs the bot using the run command using the token given in the config"""

        if not self.config.token:
            logger.critical("Token is missing! Please check the config file")
            sys.exit(1)
        else:
            self.run(self.config.token)

    async def close(self) -> None:
        self.db_client.close()

        await super().close()

    async def on_ready(self) -> None:
        pyver = sys.version_info
        logger.info("Powered by Python %d.%d.%d", pyver.major, pyver.minor, pyver.micro)
        logger.info("Using discord.py %s", discord.__version__)
        logger.info("Logged in as %s (%d)", self.user.name, self.user.id)
        logger.info("Connected to:")
        logger.info("* %d guilds", len(self.guilds))
        logger.info("* %d channels", sum(1 for _ in self.get_all_channels()))
        logger.info("* %d users", len(self.users))
        logger.info("------")
        logger.info("Ready!")
