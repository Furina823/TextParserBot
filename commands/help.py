import discord
from discord.ext import commands

from config import CHANNEL_ID


def setup(bot: commands.Bot):
    async def english_commands_response(interaction: discord.Interaction):
        embed = discord.Embed(
            title="Bot Commands",
            description=(
                f"Upload `.txt` save files in <#{CHANNEL_ID}>.\n"
                "Use these commands to search records, manage bindings, and review updates."
            ),
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Search Records",
            value=(
                "**/getcode-username**\n"
                "Find all saved characters for one game ID. Input: `username`\n\n"
                "**/getcode-class**\n"
                "Find all players using one class. Input: `class_name`\n\n"
                "**/statistic-record**\n"
                "Show bound members with the tracked role and each character's latest update date."
            ),
            inline=False
        )
        embed.add_field(
            name="Binding Notice",
            value=(
                "`username` is the game ID/player name inside the uploaded text file.\n"
                "`user` is the Discord account that owns it.\n\n"
                "If `junxuan823#4896` is bound to `junx`, and someone else uploads a save for "
                "`junxuan823#4896`, the bot mentions `junx` so the owner knows their data was updated."
            ),
            inline=False
        )
        embed.add_field(
            name="Binding Commands",
            value=(
                "**/bind-user**\n"
                "Bind a game ID to a Discord user. Inputs: `username`, `user`\n\n"
                "**/unbind-user**\n"
                "Remove a game ID binding. Input: `username`\n\n"
                "**/show-bindings**\n"
                "Show every current game ID binding.\n\n"
                "**/whois**\n"
                "Check which Discord user a game ID is bound to. Input: `username`"
            ),
            inline=False
        )
        embed.add_field(
            name="Admin",
            value=(
                "**/delete-user**\n"
                "Delete all saved characters for one game ID. Input: `username`\n\n"
                "**/delete-character**\n"
                "Delete one saved character. Inputs: `username`, `class_name`"
            ),
            inline=False
        )
        embed.add_field(
            name="Help",
            value=(
                "**/commands**\n"
                "Show this command list and expected usage."
            ),
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def chinese_commands_response(interaction: discord.Interaction):
        embed = discord.Embed(
            title="指令列表",
            description=(
                f"請在 <#{CHANNEL_ID}> 上傳 `.txt` 存檔。\n"
                "使用以下指令查詢記錄、管理綁定與查看更新。"
            ),
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="查詢記錄",
            value=(
                "**/id檔**\n"
                "依玩家 ID 查詢所有已儲存角色。輸入：`username`\n\n"
                "**/角色檔**\n"
                "依職業查詢所有玩家。輸入：`class_name`\n\n"
                "**/統計記錄**\n"
                "查看已綁定且擁有指定身分組玩家的角色最新更新日期。"
            ),
            inline=False
        )
        embed.add_field(
            name="綁定說明",
            value=(
                "`username` 代表上傳文字檔裡的遊戲 ID／玩家名稱。\n"
                "`user` 代表 Discord 使用者／帳號。\n\n"
                "如果 `junxuan823#4896` 已綁定到 `junx`，其他人上傳玩家名稱為 "
                "`junxuan823#4896` 的文字檔時，系統會提及 `junx`，通知真正持有人資料已被更新。"
            ),
            inline=False
        )
        embed.add_field(
            name="綁定指令",
            value=(
                "**/綁定**\n"
                "將遊戲 ID 綁定到 Discord 使用者。輸入：`username`、`user`\n\n"
                "**/解除綁定**\n"
                "解除玩家 ID 綁定。輸入：`username`\n\n"
                "**/查看綁定**\n"
                "查看目前所有玩家 ID 綁定。"
            ),
            inline=False
        )
        embed.add_field(
            name="管理員",
            value=(
                "**/刪除記錄**\n"
                "刪除指定玩家 ID 的所有已儲存角色。輸入：`username`"
            ),
            inline=False
        )
        embed.add_field(
            name="說明",
            value=(
                "**/指令**\n"
                "顯示指令列表與使用方式。"
            ),
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(
        name="commands",
        description="Show all bot commands and how to use them"
    )
    async def commands_list(interaction: discord.Interaction):
        await english_commands_response(interaction)

    @bot.tree.command(
        name="指令",
        description="顯示所有指令與使用方式"
    )
    async def commands_list_zh(interaction: discord.Interaction):
        await chinese_commands_response(interaction)
