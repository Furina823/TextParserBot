import discord
from discord import app_commands
from discord.ext import commands

from database import set_binding, remove_binding, get_binding
from config import ADMIN_IDS


def admin_only():
    """Check that user is in ADMIN_IDS; if empty, fall back to Discord admin permission."""
    def predicate(interaction: discord.Interaction) -> bool:
        if ADMIN_IDS:
            return interaction.user.id in ADMIN_IDS
        return bool(getattr(interaction.user, "guild_permissions", None) and interaction.user.guild_permissions.administrator)
    return app_commands.check(predicate)


def setup(bot: commands.Bot):
    @bot.tree.command(
        name="bind-user",
        description="Bind a Player ID to a Discord user (Admin only)(綁定玩家ID)"
    )
    @admin_only()
    @app_commands.describe(username="玩家ID", user="要綁定的 Discord 使用者")
    async def bind_user(interaction: discord.Interaction, username: str, user: discord.Member):
        set_binding(interaction.guild_id, username, user.id)
        await interaction.response.send_message(
            f"✅ Bound **{username}** → {user.mention}",
            ephemeral=True
        )

    @bot.tree.command(
        name="unbind-user",
        description="Remove binding for a Player ID (Admin only)(解除玩家ID綁定)"
    )
    @admin_only()
    @app_commands.describe(username="玩家ID")
    async def unbind_user(interaction: discord.Interaction, username: str):
        existed = remove_binding(interaction.guild_id, username)
        if not existed:
            return await interaction.response.send_message(
                f"❌ No binding found for: **{username}** (沒有找到綁定)",
                ephemeral=True
            )
        await interaction.response.send_message(
            f"✅ Unbound: **{username}** (已解除綁定)",
            ephemeral=True
        )

    @bot.tree.command(
        name="whois",
        description="Show who a Player ID is bound to(查詢玩家ID綁定)"
    )
    @app_commands.describe(username="玩家ID")
    async def whois(interaction: discord.Interaction, username: str):
        bound_id = get_binding(interaction.guild_id, username)
        if not bound_id:
            return await interaction.response.send_message(
                f"❌ Not bound: **{username}** (尚未綁定)",
                ephemeral=True
            )
        await interaction.response.send_message(
            f"🔗 **{username}** → <@{bound_id}>",
            ephemeral=True
        )

