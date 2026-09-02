from datetime import datetime

import discord
from discord.ext import commands

from commands.checks import command_access_only
from config import STATISTICS_ROLE_ID
from database import load_bindings, load_db, normalize_username
from parser import CLASS_TRANSLATIONS


def _parse_upload_time(value: str):
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError):
        return None


def _format_upload_date(value: str) -> str:
    parsed = _parse_upload_time(value)
    if not parsed:
        return value or "Unknown"
    return f"{parsed.day}-{parsed.month}-{parsed.year}"


def _latest_character_rows(entries: list[dict], chinese: bool) -> list[str]:
    latest_by_class = {}
    for entry in entries:
        class_name = entry.get("class", "Unknown")
        uploaded_at = entry.get("uploaded_at", "")
        parsed = _parse_upload_time(uploaded_at)
        current = latest_by_class.get(class_name)
        if not current or (parsed or datetime.min) > (current[0] or datetime.min):
            latest_by_class[class_name] = (parsed, uploaded_at)

    rows = []
    for class_name, (_, uploaded_at) in sorted(latest_by_class.items()):
        display = CLASS_TRANSLATIONS.get(class_name, class_name) if chinese else class_name
        separator = "更新於" if chinese else "Updated In"
        rows.append(f"- {display} {separator} {_format_upload_date(uploaded_at)}")
    return rows


def _chunk_text(lines: list[str], limit: int = 1024) -> list[str]:
    chunks = []
    current = ""
    for line in lines:
        next_value = line if not current else f"{current}\n{line}"
        if len(next_value) > limit and current:
            chunks.append(current)
            current = line
        else:
            current = next_value
    if current:
        chunks.append(current)
    return chunks


async def _get_bound_role_records(guild: discord.Guild):
    db = load_db(guild.id)
    bindings = load_bindings(guild.id)

    entries_by_username = {}
    canonical_usernames = {}
    for entry in db:
        username = entry.get("username")
        if not username:
            continue
        key = normalize_username(username)
        entries_by_username.setdefault(key, []).append(entry)
        canonical_usernames.setdefault(key, username)

    records = []
    seen_members = {}
    for username_key, discord_id in sorted(bindings.items()):
        try:
            discord_id = int(discord_id)
        except (TypeError, ValueError):
            continue

        try:
            member = seen_members.get(discord_id)
            if member is None:
                member = guild.get_member(discord_id) or await guild.fetch_member(discord_id)
                seen_members[discord_id] = member
        except (discord.NotFound, discord.HTTPException):
            continue

        if not any(role.id == STATISTICS_ROLE_ID for role in member.roles):
            continue

        normalized_key = normalize_username(username_key)
        records.append({
            "username": canonical_usernames.get(normalized_key, username_key),
            "member": member,
            "entries": entries_by_username.get(normalized_key, []),
        })

    return records


def _build_embeds(records: list[dict], chinese: bool) -> list[discord.Embed]:
    title = "統計記錄" if chinese else "Statistic Record"
    description = (
        f"以下只顯示擁有 <@&{STATISTICS_ROLE_ID}> 身分組且已完成綁定的玩家。"
        if chinese else
        f"Only members with <@&{STATISTICS_ROLE_ID}> and an existing binding are shown."
    )
    empty_text = "目前沒有符合條件的綁定記錄。" if chinese else "No matching bound records found."
    no_records_text = "尚未有角色記錄。" if chinese else "No character records yet."

    if not records:
        embed = discord.Embed(title=title, description=empty_text, color=discord.Color.blurple())
        return [embed]

    embeds = []
    current_embed = discord.Embed(title=title, description=description, color=discord.Color.blurple())

    def push_embed():
        nonlocal current_embed
        embeds.append(current_embed)
        current_embed = discord.Embed(title=title, color=discord.Color.blurple())

    for record in records:
        rows = _latest_character_rows(record["entries"], chinese) or [no_records_text]
        for index, value in enumerate(_chunk_text(rows)):
            if len(current_embed.fields) >= 25:
                push_embed()
            field_name = record["username"] if index == 0 else f"{record['username']} (continued)"
            current_embed.add_field(name=field_name, value=value, inline=False)

    embeds.append(current_embed)
    return embeds


def setup(bot: commands.Bot):
    async def statistics_response(interaction: discord.Interaction, chinese: bool = False):
        if interaction.guild is None:
            message = "這個指令只能在伺服器內使用。" if chinese else "This command can only be used in a server."
            return await interaction.response.send_message(message, ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        records = await _get_bound_role_records(interaction.guild)
        embeds = _build_embeds(records, chinese)

        await interaction.followup.send(embed=embeds[0], ephemeral=True)
        for embed in embeds[1:]:
            await interaction.followup.send(embed=embed, ephemeral=True)

    @bot.tree.command(
        name="statistic-record",
        description="Show latest character update dates for bound members with the tracked role"
    )
    @command_access_only()
    async def statistic_record(interaction: discord.Interaction):
        await statistics_response(interaction, chinese=False)

    @bot.tree.command(
        name="統計記錄",
        description="查看已綁定且擁有指定身分組玩家的角色更新日期"
    )
    @command_access_only()
    async def statistic_record_zh(interaction: discord.Interaction):
        await statistics_response(interaction, chinese=True)
