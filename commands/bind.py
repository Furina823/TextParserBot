import discord
from discord import app_commands
from discord.ext import commands

from database import set_binding, remove_binding, get_binding, load_bindings


def setup(bot: commands.Bot):
    @bot.tree.command(
        name="bind-user",
        description="Bind a Player ID to a Discord user (綁定玩家ID)"
    )
    @app_commands.describe(username="玩家ID", user="要綁定的 Discord 使用者")
    async def bind_user(interaction: discord.Interaction, username: str, user: discord.Member):
        set_binding(interaction.guild_id, username, user.id)
        await interaction.response.send_message(
            f"✅ Bound **{username}** → {user.mention} (已綁定)",
            ephemeral=True
        )

    @bot.tree.command(
        name="unbind-user",
        description="Remove binding for a Player ID (解除玩家ID綁定)"
    )
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
        name="show-bindings",
        description="Show all current Player ID bindings (顯示所有綁定列表)"
    )
    async def show_bindings(interaction: discord.Interaction):
        bindings = load_bindings(interaction.guild_id)
        if not bindings:
            return await interaction.response.send_message(
                "📭 No bindings found. (目前沒有任何綁定)",
                ephemeral=True
            )
        lines = [f"🔗 **{username}** → <@{discord_id}>" for username, discord_id in sorted(bindings.items())]
        await interaction.response.send_message(
            "**Binding List (綁定列表):**\n" + "\n".join(lines),
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
