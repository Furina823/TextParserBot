import discord
from discord import app_commands
from discord.ext import commands

from config import CHANNEL_ID, COMMAND_ROLE_ID


class CommandAccessDenied(app_commands.CheckFailure):
    pass


def _is_chinese_command(interaction: discord.Interaction) -> bool:
    command_name = getattr(getattr(interaction, "command", None), "name", "")
    return any("\u4e00" <= char <= "\u9fff" for char in command_name)


def _is_upload_channel(interaction: discord.Interaction) -> bool:
    channel_id = getattr(interaction, "channel_id", None)
    if channel_id is None and interaction.channel is not None:
        channel_id = interaction.channel.id
    return channel_id == CHANNEL_ID


def _has_command_role(interaction: discord.Interaction) -> bool:
    roles = getattr(interaction.user, "roles", [])
    return any(role.id == COMMAND_ROLE_ID for role in roles)


def has_command_access(interaction: discord.Interaction) -> bool:
    return (
        interaction.guild is not None
        and _is_upload_channel(interaction)
        and _has_command_role(interaction)
    )


def command_access_only():
    async def predicate(interaction: discord.Interaction) -> bool:
        if not has_command_access(interaction):
            raise CommandAccessDenied()
        return True

    return app_commands.check(predicate)


async def send_access_denied(interaction: discord.Interaction):
    if _is_chinese_command(interaction):
        message = f"請在 <#{CHANNEL_ID}> 使用此指令，並且你需要擁有 <@&{COMMAND_ROLE_ID}> 身分組。"
    else:
        message = f"Please use this command in <#{CHANNEL_ID}> and make sure you have the <@&{COMMAND_ROLE_ID}> role."

    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


def setup(bot: commands.Bot):
    @bot.tree.error
    async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, CommandAccessDenied):
            return await send_access_denied(interaction)

        if isinstance(error, app_commands.CheckFailure):
            if _is_chinese_command(interaction):
                message = "你沒有權限使用此指令。"
            else:
                message = "You do not have permission to use this command."

            if interaction.response.is_done():
                return await interaction.followup.send(message, ephemeral=True)
            return await interaction.response.send_message(message, ephemeral=True)

        raise error
