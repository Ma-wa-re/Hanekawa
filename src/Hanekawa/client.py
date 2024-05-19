import logging
import sys
from datetime import datetime, timedelta

import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .config import Config
from .settings_db import SettingsTable

logger = logging.getLogger(__name__)

EXTENSIONS = ["Hanekawa.extensions.misc", "Hanekawa.extensions.reporting"]


class Bot(commands.Bot):
    __slots__ = (
        "config",
        "start_time",
    )

    def __init__(self, config: Config):
        self.config: Config = config
        self.start_time: datetime = datetime.now()
        self.db_client: AsyncIOMotorClient = AsyncIOMotorClient(self.config.database_url)
        self.db: AsyncIOMotorDatabase | None = None
        self.settings_table: SettingsTable | None

        super().__init__(
            command_prefix=commands.when_mentioned,
            description="Hanekawa - To fill out later",
            intents=discord.Intents.default(),
            help_command=None,
        )

    @property
    def uptime(self) -> timedelta:
        """Gets bot's uptime"""

        return datetime.now() - self.start_time

    def run_with_token(self) -> None:
        """Runs the bot using the run command using the token given in the config"""

        if not self.config.token:
            logger.critical("Token is missing! Please check the config file")
            sys.exit(1)
        else:
            self.run(self.config.token)

    async def close(self) -> None:
        """On close of the discord connect also close the connection to the DB"""
        self.db_client.close()

        await super().close()

    async def setup_hook(self) -> None:
        # Connect to DB
        logger.debug(await self.db_client.list_database_names())
        self.db = self.db_client.hanekawa
        self.settings_table = SettingsTable(self.db)

        # Load the extensions
        for extension in EXTENSIONS:
            logger.info(f"Loading extension: {extension}")
            await self.load_extension(extension)

        # Sync to dev guild if one is configured
        if self.config.dev_guild:
            guild = discord.Object(self.config.dev_guild)
            self.tree.copy_global_to(guild=guild)
            # followed by syncing to the testing guild.
            await self.tree.sync(guild=guild)

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
