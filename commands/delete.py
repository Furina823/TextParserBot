# commands/delete.py
import discord
from discord import app_commands
from discord.ext import commands
from database import load_db, delete_character as db_delete_character, delete_user as db_delete_user
from parser import get_class_display, CLASS_TRANSLATIONS
from config import ADMIN_IDS


def admin_only():
    """Check that user is in ADMIN_IDS; if empty, fall back to Discord admin permission."""
    def predicate(interaction: discord.Interaction) -> bool:
        if ADMIN_IDS:
            return interaction.user.id in ADMIN_IDS
        # Fallback: allow server admins when ADMIN_IDS is not configured
        return bool(getattr(interaction.user, "guild_permissions", None) and interaction.user.guild_permissions.administrator)
    return app_commands.check(predicate)


def setup(bot: commands.Bot):
    # ===== COMMAND: DELETE CHARACTER =====
    @bot.tree.command(
        name="delete-character",
        description="Delete a specific character (Admin only)(刪除指定角色)"
    )
    @app_commands.describe(username="玩家ID", class_name="職業名稱")
    @admin_only()
    async def delete_character(interaction: discord.Interaction, username: str, class_name: str):
        success = db_delete_character(interaction.guild_id, username, class_name)
        
        if not success:
            return await interaction.response.send_message(
                f"❌ Character not found: {username} - {get_class_display(class_name)} (沒有找到角色)", 
                ephemeral=True
            )
        
        await interaction.response.send_message(
            f"✅ Deleted: **{username}** - {get_class_display(class_name)} (已刪除)", 
            ephemeral=True
        )

    # ===== COMMAND: DELETE USER =====
    @bot.tree.command(
        name="delete-user",
        description="Delete ALL characters for a username (Admin only)(刪除玩家紀錄)"
    )
    @app_commands.describe(username="玩家ID")
    @admin_only()
    async def delete_user(interaction: discord.Interaction, username: str):
        count = db_delete_user(interaction.guild_id, username)
        
        if count == 0:
            return await interaction.response.send_message(
                f"❌ No characters found for: {username} (沒有找到任何角色)", 
                ephemeral=True
            )
        
        await interaction.response.send_message(
            f"✅ Deleted **{count}** character(s) for: **{username}** (已刪除以上角色)", 
            ephemeral=True
        )

    # ===== AUTOCOMPLETES =====
    @delete_character.autocomplete('username')
    async def delete_char_username_autocomplete(interaction: discord.Interaction, current: str):
        db = load_db(interaction.guild_id)
        usernames = sorted({entry["username"] for entry in db if "username" in entry})
        
        return [
            app_commands.Choice(name=name, value=name)
            for name in usernames if current.lower() in name.lower()
        ][:25]

    @delete_character.autocomplete('class_name')
    async def delete_char_class_autocomplete(interaction: discord.Interaction, current: str):
        db = load_db(interaction.guild_id)

        username = getattr(interaction.namespace, "username", None)
        if not username:
            return []

        # Get only classes that this username actually has
        user_classes = sorted({
            entry["class"]
            for entry in db
            if entry["username"].lower() == username.lower()
        })

        return [
            app_commands.Choice(name=get_class_display(c), value=c)
            for c in user_classes
            if current.lower() in c.lower() or current in CLASS_TRANSLATIONS.get(c, "")
        ][:25]
