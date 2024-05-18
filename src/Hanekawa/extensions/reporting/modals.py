import logging
import discord
from motor.motor_asyncio import AsyncIOMotorCollection

logger = logging.getLogger(__name__)


class FourmChannelSelect(discord.ui.ChannelSelect):
    def __init__(self, settings_table: AsyncIOMotorCollection):
        self.settings_table = settings_table
        super().__init__(channel_types=[discord.ChannelType.forum])

    async def callback(self, interaction: discord.Interaction):
        # Check that the fourm channel has the tags needed
        fourm = await self.values[0].fetch()

        fourm_tags = [str(tag) for tag in fourm.available_tags]

        if not set(["report", "feedback"]).issubset(fourm_tags):
            await interaction.response.send_message(
                content=f"{fourm.mention} does not have the tags needed. (report & feedback)", ephemeral=True
            )

        # Check settings table for existing config
        settings_entry = await self.settings_table.find_one({"guild_id": interaction.guild_id})

        if settings_entry:
            logger.info(f"Updating setting config for reporing for {interaction.guild_id}")
            _id = settings_entry.pop("_id")
            settings_entry["report_channel"] = fourm.id
            await self.settings_table.replace_one({"_id": _id}, settings_entry)
        else:
            logger.info(f"Creating setting config for reporing for {interaction.guild_id}")
            await self.settings_table.insert_one({"guild_id": interaction.guild_id, "report_channel": fourm.id})

        await interaction.response.send_message(
            content=f"{fourm.mention} has been configured as the report channel", ephemeral=True
        )


class FourmChannelView(discord.ui.View):
    def __init__(self, settings_table: AsyncIOMotorCollection):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(FourmChannelSelect(settings_table=settings_table))


class MessageReport(discord.ui.Modal, title="Message Report"):
    def __init__(self, settings_table: AsyncIOMotorCollection, message: discord.Message):
        self.settings_table = settings_table
        self.message = message

        super().__init__()

    report = discord.ui.TextInput(
        label="Reason for reporting this message",
        style=discord.TextStyle.long,
        placeholder="Type your reason here...",
        required=True,
        max_length=500,
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Check settings table for existing config and get fourm channel
        try:
            settings_entry = await self.settings_table.find_one({"guild_id": interaction.guild_id})
            logger.info(settings_entry)
            if settings_entry:
                if "report_channel" in settings_entry:
                    fourm = interaction.client.get_channel(settings_entry["report_channel"])

                    logger.info(fourm.name)
                    if fourm:
                        tag = [tag for tag in fourm.available_tags if tag.name == "report"][0]
                        embed = discord.Embed(title="Reported Message")
                        embed.description = self.message.clean_content
                        embed.set_author(name=self.message.author.name, icon_url=self.message.author.avatar.url)
                        embed.add_field(
                            name="Message Created At", value=f"<t:{self.message.created_at.strftime('%s')}:F>"
                        )
                        embed.add_field(name="Reported At", value=f"<t:{interaction.created_at.strftime('%s')}:F>")
                        embed.add_field(name="Reported By", value=interaction.user.mention)
                        embed.add_field(name="Reason", value=self.report.value)

                        thread, message = await fourm.create_thread(
                            name=f"Message Report: {self.message.id}",
                            auto_archive_duration=1440,
                            applied_tags=[tag],
                            embed=embed,
                        )

                    await interaction.response.send_message(
                        "Thanks for the report!, Staff will get back to you about this", ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        "Reports have not been setup yet, Please get an admin to configure", ephemeral=True
                    )
            else:
                await interaction.response.send_message(
                    "Reports have not been setup yet, Please get an admin to configure", ephemeral=True
                )
        except Exception:
            logger.exception("Report failed")
            raise

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message("Oops! Something went wrong. Please let the staff know", ephemeral=True)


class UserReport(discord.ui.Modal, title="User Report"):
    def __init__(self, settings_table: AsyncIOMotorCollection, user: discord.Member):
        self.settings_table = settings_table
        self.user = user

        super().__init__()

    report = discord.ui.TextInput(
        label="Reason for reporting this User",
        style=discord.TextStyle.long,
        placeholder="Type your reason here...",
        required=True,
        max_length=500,
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Check settings table for existing config and get fourm channel
        try:
            settings_entry = await self.settings_table.find_one({"guild_id": interaction.guild_id})
            logger.info(settings_entry)
            if settings_entry:
                if "report_channel" in settings_entry:
                    fourm = interaction.client.get_channel(settings_entry["report_channel"])

                    logger.info(fourm.name)
                    if fourm:
                        tag = [tag for tag in fourm.available_tags if tag.name == "report"][0]
                        embed = discord.Embed(title="Reported User")
                        embed.set_author(name=self.user.name, icon_url=self.user.avatar.url)
                        embed.add_field(name="Reported At", value=f"<t:{interaction.created_at.strftime('%s')}:F>")
                        embed.add_field(name="Reported By", value=interaction.user.mention)
                        embed.add_field(name="Reason", value=self.report.value)

                        thread, message = await fourm.create_thread(
                            name=f"User Report: {self.user.name} ({self.user.id})",
                            auto_archive_duration=1440,
                            applied_tags=[tag],
                            embed=embed,
                        )

                    await interaction.response.send_message(
                        "Thanks for the report!, Staff will get back to you about this", ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        "Reports have not been setup yet, Please get an admin to configure", ephemeral=True
                    )
            else:
                await interaction.response.send_message(
                    "Reports have not been setup yet, Please get an admin to configure", ephemeral=True
                )
        except Exception:
            logger.exception("Report failed")
            raise

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message("Oops! Something went wrong. Please let the staff know", ephemeral=True)
