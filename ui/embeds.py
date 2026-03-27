# ui/embeds.py
import math
import re
import discord
from discord.ui import Button
from ui.views import TimedView
from parser import get_class_display

async def show_character_details(interaction, entry):
    """Show character details with item buttons"""
    load_codes = entry.get("load_codes") or []
    uploaded_info = f"Last updated by: {entry.get('uploaded_by', 'Unknown')}\nDate: {entry.get('uploaded_at', 'Unknown')}"
    
    class_display = get_class_display(entry['class'])
    
    embed = discord.Embed(title=f"👤 {entry['username']}", color=discord.Color.gold())
    embed.add_field(name="Class (職業)", value=class_display, inline=False)
    embed.add_field(name="Version Info", value=f"Played(遊玩版本): {entry['played_version']}\nCompat(版本相容): {entry['compatible_version']}", inline=True)
    embed.add_field(name="Upload Info(上傳)", value=uploaded_info, inline=True)

    view = TimedView(timeout=300)
    
    def make_items_embed(section: str = "inventory", storage_page: int = 0) -> discord.Embed:
        """Create an items embed for a single section (inventory / bag / storage)."""
        inv_items = entry.get("inventory") or []
        bag_items = entry.get("bag") or []
        storage_items = entry.get("storage") or []

        embed = discord.Embed(
            title=f"📦 Items for {entry['username']}",
            color=discord.Color.blurple(),
        )

        def _strip_leading_number(s: str) -> str:
            # Items sometimes already include "12. " / "12) " / "12 - " prefixes.
            return re.sub(r"^\s*\d+\s*[\.\)\-]\s*", "", s).strip()

        def add_section_fields(title_prefix: str, raw_items, page: int | None = None, per_page: int = 20):
            if not raw_items:
                embed.add_field(name=title_prefix, value="_Empty_", inline=False)
                return

            items = raw_items
            total_pages = 1
            idx_offset = 0

            if page is not None:
                total_pages = max(1, math.ceil(len(raw_items) / per_page))
                page = max(0, min(page, total_pages - 1))
                start = page * per_page
                end = start + per_page
                items = raw_items[start:end]
                idx_offset = start

            cleaned_items = [_strip_leading_number(str(name)) for name in items]
            nums = [f"{idx_offset + i}. {name}" for i, name in enumerate(cleaned_items, start=1)]

            # Split into up to 2 columns to keep line length similar to Version/Upload fields
            mid = (len(nums) + 1) // 2
            left = "\n".join(nums[:mid]) or "_Empty_"
            right = "\n".join(nums[mid:]) if len(nums) > mid else ""

            title = title_prefix
            if page is not None and total_pages > 1:
                title = f"{title_prefix} – Page {page + 1}/{total_pages}"

            embed.add_field(name=title, value=left[:1024], inline=True)
            if right:
                embed.add_field(name="\u200b", value=right[:1024], inline=True)

        if section == "inventory":
            add_section_fields("📦 Inventory (裝備)", inv_items)
        elif section == "bag":
            add_section_fields("🎒 Bag (背包)", bag_items)
        else:  # storage
            add_section_fields("🗄️ Storage (倉庫)", storage_items, page=storage_page, per_page=20)

        total_items = len(inv_items) + len(bag_items) + len(storage_items)
        embed.set_footer(text=f"Total: {total_items} items")
        return embed

    def make_items_view(section: str = "inventory", storage_page: int = 0) -> TimedView:
        """Create a view with section tabs and optional storage pagination."""
        items_view = TimedView(timeout=300)

        # Section buttons (tabs)
        sections = [
            ("inventory", "📦 Inventory"),
            ("bag", "🎒 Bag"),
            ("storage", "🗄️ Storage"),
        ]

        for key, label in sections:
            style = discord.ButtonStyle.primary if key == section else discord.ButtonStyle.secondary
            btn = Button(label=label, style=style)

            async def sec_cb(inter, _sec=key):
                new_page = storage_page if _sec == "storage" else 0
                await inter.response.edit_message(
                    embed=make_items_embed(_sec, new_page),
                    view=make_items_view(_sec, new_page),
                )

            btn.callback = sec_cb
            items_view.add_item(btn)

        # Storage pagination (only when viewing storage)
        if section == "storage":
            storage_items = entry.get("storage") or []
            per_page = 20
            total_pages = max(1, math.ceil(len(storage_items) / per_page))

            if total_pages > 1:
                if storage_page > 0:
                    prev_btn = Button(label="⬅️", style=discord.ButtonStyle.secondary)

                    async def prev_cb(inter, _page=storage_page - 1):
                        await inter.response.edit_message(
                            embed=make_items_embed("storage", _page),
                            view=make_items_view("storage", _page),
                        )

                    prev_btn.callback = prev_cb
                    items_view.add_item(prev_btn)

                if storage_page < total_pages - 1:
                    next_btn = Button(label="➡️", style=discord.ButtonStyle.secondary)

                    async def next_cb(inter, _page=storage_page + 1):
                        await inter.response.edit_message(
                            embed=make_items_embed("storage", _page),
                            view=make_items_view("storage", _page),
                        )

                    next_btn.callback = next_cb
                    items_view.add_item(next_btn)

        return items_view

    # Quiet bot: only allow private item viewing
    private_button = Button(label="👁️ Show Items (查詢裝備)", style=discord.ButtonStyle.secondary)
    async def show_items_private(inter):
        await inter.response.send_message(
            embed=make_items_embed("inventory", 0),
            view=make_items_view("inventory", 0),
            ephemeral=True,
        )

    private_button.callback = show_items_private
    view.add_item(private_button)
    
    # Quiet bot: info panel is only visible to the user
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    view.message = await interaction.original_response()

    # Automatically show load codes in an ephemeral message (previously via "Copy Load Codes" button)
    if load_codes:
        max_codes = 25
        codes = load_codes[:max_codes]
        parts = []
        for i, code in enumerate(codes, start=1):
            parts.append(f"Load Code #{i}\n```{code}```")
        content = "\n".join(parts)
        try:
            await interaction.followup.send(content, ephemeral=True)
        except Exception:
            pass

def create_grid_embed(title, items, page, is_class_search):
    """Create a 3x3 grid embed for character/player listing"""
    items_per_page = 9
    start = page * items_per_page
    end = start + items_per_page
    current_items = items[start:end]
    
    embed = discord.Embed(title=title, color=discord.Color.blue())
    embed.set_footer(text=f"Page {page + 1} • Total: {len(items)}")

    for item in current_items:
        name = item["entry"]["username"] if is_class_search else item["full_name"]
        embed.add_field(name=name, value=f"📅 {item['date']}", inline=True)
    
    # Fill remaining slots to maintain 3-column layout
    while len(embed.fields) % 3 != 0 and len(embed.fields) > 0:
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        
    return embed, len(items) > end