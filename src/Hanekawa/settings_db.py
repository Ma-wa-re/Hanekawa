import logging
from typing import Annotated, Optional

from bson import ObjectId as _ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pydantic import BaseModel, Field, ValidationError
from pydantic.functional_validators import AfterValidator

logger = logging.getLogger(__name__)


# Function to check the the id value in Settings record is a bson.ObjectId
def _check_object_id(value: str) -> str:
    if not _ObjectId.is_valid(value):
        raise ValueError("Invalid ObjectId")
    return value


# New ObjectId for bson.ObjectId what validates for Pydantic
ObjectId = Annotated[str, AfterValidator(_check_object_id)]


class SettingsRecord(BaseModel):
    id: Optional[ObjectId] = Field(None, exclude=True)
    guild_id: int
    report_channel: Optional[int] = None


class SettingsTable:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        self._table: AsyncIOMotorCollection = self._db.settings

    async def get(self, guild_id: int) -> Optional[SettingsRecord]:
        """Gets a guilds setting config if any from a guild_id

        Parameters
        -----------
        guild_id: :class:`int`
            The ID of the guild

        Returns
        --------
        Optional[:class:`SettingsRecord`]
            Returns the guilds settings or None

        """

        # Do a find_one on tehe settings table as see if there is a record for the guild
        logger.info(f"Getting settings record for {guild_id}")
        record = await self._table.find_one({"guild_id": guild_id})

        if record:
            # The _id in the record needs to be id in settings record so we set that and remove _id
            record["id"] = str(record["_id"])
            del record["_id"]

            try:
                return SettingsRecord(**record)
            except ValidationError:
                logger.exception("Record from DB doesn't match SettingRecord, returning None")
                return None
        return None

    async def set(self, record: SettingsRecord) -> SettingsRecord:
        """Sets a guilds setting config in the DB

        Parameters
        -----------
        guild_id: :class:`SettingsRecord`
            The record of the guilds settings you want to create or update

        Returns
        --------
        :class:`SettingsRecord`
            Returns the update guild record

        """

        if record.id:
            logger.info(f"Updating record for {record.guild_id}")
            await self._table.replace_one({"_id": _ObjectId(record.id)}, record.model_dump())
            return record
        else:
            logger.info(f"Creating record for {record.guild_id}")
            status = await self._table.insert_one(record.model_dump())
            record.id = str(status.inserted_id)
            return record
