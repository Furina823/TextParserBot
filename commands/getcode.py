# commands/getcode.py
import discord
from discord import app_commands
from discord.ext import commands
from database import load_db
from parser import get_class_display, CLASS_TRANSLATIONS

def setup(bot: commands.Bot):
    # ===== COMMAND: GET BY USERNAME =====
    @bot.tree.command(name="getcode-username", description="Search characters by Player ID(搜尋玩家存檔 ID)")
    @app_commands.describe(username="輸入玩家ID")
    async def getcode_username(interaction: discord.Interaction, username: str):
        db = load_db(interaction.guild_id)
        results = [e for e in db if e["username"].lower() == username.lower()]

        if not results:
            return await interaction.response.send_message("❌ No data found. (查無資料)", ephemeral=True)

        # If only one character, jump straight to the details page.
        if len(results) == 1:
            from ui.embeds import show_character_details  # import here to avoid circular import
            return await show_character_details(interaction, results[0])

        table_items = [{
            "full_name": get_class_display(e["class"]),
            "date": e["uploaded_at"].split()[0],
            "entry": e
        } for e in results]

        # Inner render function for pagination
        async def render(inter, page=0, edit=False):
            from ui.embeds import create_grid_embed, show_character_details  # import here to avoid circular import
            from ui.views import TimedView
            embed, has_next = create_grid_embed(f"Characters for {username}", table_items, page, False)
            view = TimedView(timeout=300)  # 5 minutes

            start = page * 9
            page_items = table_items[start:start+9]
            select = discord.ui.Select(
                placeholder="Select character...",
                options=[discord.SelectOption(label=item["full_name"][:100], value=str(i + start)) 
                         for i, item in enumerate(page_items)]
            )

            async def sel_cb(sel_inter):
                await show_character_details(sel_inter, table_items[int(select.values[0])]["entry"])

            select.callback = sel_cb
            view.add_item(select)

            if page > 0:
                btn = discord.ui.Button(label="⬅️", style=discord.ButtonStyle.secondary)
                btn.callback = lambda i: render(i, page - 1, True)
                view.add_item(btn)
            if has_next:
                btn = discord.ui.Button(label="➡️", style=discord.ButtonStyle.secondary)
                btn.callback = lambda i: render(i, page + 1, True)
                view.add_item(btn)

            if edit:
                await inter.response.edit_message(embed=embed, view=view)
                view.message = await inter.original_response()
            else:
                await inter.response.send_message(embed=embed, view=view, ephemeral=True)
                view.message = await inter.original_response()

        await render(interaction)

    # ===== COMMAND: GET BY CLASS =====
    @bot.tree.command(name="getcode-class", description="Search players by Class(搜尋該職業玩家)")
    @app_commands.describe(class_name="輸入職業名稱")
    async def getcode_class(interaction: discord.Interaction, class_name: str):
        db = load_db(interaction.guild_id)
        results = [e for e in db if e["class"] == class_name]

        if not results:
            return await interaction.response.send_message("❌ No data found. (查無資料)", ephemeral=True)

        # If only one player for this class, jump straight to details
        if len(results) == 1:
            from ui.embeds import show_character_details  # avoid circular import
            return await show_character_details(interaction, results[0])

        table_items = [{"date": e["uploaded_at"].split()[0], "entry": e} for e in results]

        async def render(inter, page=0, edit=False):
            from ui.embeds import create_grid_embed, show_character_details
            from ui.views import TimedView
            embed, has_next = create_grid_embed(f"Players: {get_class_display(class_name)}", table_items, page, True)
            view = TimedView(timeout=300)  # 5 minutes

            start = page * 9
            page_items = table_items[start:start+9]
            select = discord.ui.Select(
                placeholder="Select player...",
                options=[discord.SelectOption(label=item["entry"]["username"], value=str(i + start))
                         for i, item in enumerate(page_items)]
            )

            async def sel_cb(sel_inter):
                await show_character_details(sel_inter, table_items[int(select.values[0])]["entry"])

            select.callback = sel_cb
            view.add_item(select)

            if page > 0:
                btn = discord.ui.Button(label="⬅️", style=discord.ButtonStyle.secondary)
                btn.callback = lambda i: render(i, page - 1, True)
                view.add_item(btn)
            if has_next:
                btn = discord.ui.Button(label="➡️", style=discord.ButtonStyle.secondary)
                btn.callback = lambda i: render(i, page + 1, True)
                view.add_item(btn)

            if edit:
                await inter.response.edit_message(embed=embed, view=view)
                view.message = await inter.original_response()
            else:
                await inter.response.send_message(embed=embed, view=view, ephemeral=True)
                view.message = await inter.original_response()

        await render(interaction)

    # ===== AUTOCOMPLETES =====
    @getcode_class.autocomplete('class_name')
    async def class_autocomplete(interaction: discord.Interaction, current: str):
        db = load_db(interaction.guild_id)

        # Only suggest classes that actually have records in this guild
        classes_in_db = sorted({e["class"] for e in db if "class" in e})
        current_lower = current.lower()

        choices = []
        for c in classes_in_db:
            display = get_class_display(c)
            # Match by raw class name or display (includes translation)
            if current_lower in c.lower() or current_lower in display.lower():
                choices.append(app_commands.Choice(name=display, value=c))

        return choices[:25]

    @getcode_username.autocomplete('username')
    async def username_autocomplete(interaction: discord.Interaction, current: str):
        db = load_db(interaction.guild_id)
        usernames = sorted(list(set(entry["username"] for entry in db if "username" in entry)))

        return [
            app_commands.Choice(name=name, value=name)
            for name in usernames if current.lower() in name.lower()
        ][:25]
