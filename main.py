# main.py
import discord
from discord.ext import commands
from config import TOKEN, CHANNEL_NAME
from database import save_to_db, get_gmt8_time, get_binding
from parser import extract_info, get_class_display

# Setup bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ===== EVENTS =====
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

@bot.event
async def on_message(message):
    if message.author.bot or message.channel.name != CHANNEL_NAME:
        return

    processed = False
    for attachment in message.attachments:
        if attachment.filename.endswith(".txt"):
            try:
                content = await attachment.read()
                data = extract_info(content.decode())
                replaced = save_to_db(data, str(message.author), get_gmt8_time(), message.guild.id)
                await message.channel.send(
                    f"✅ Data saved: **{data['username']}** ({get_class_display(data['class'])}) (資料已儲存)", 
                    delete_after=10
                )

                # Notify binder if someone else uploaded a new version (replaced existing record)
                try:
                    bound_id = get_binding(message.guild.id, data["username"])
                    if replaced and bound_id and bound_id != message.author.id:
                        await message.channel.send(
                            f"<@{bound_id}> ⚠️ New upload for **{data['username']}** "
                            f"({get_class_display(data['class'])}) by {message.author.mention} (有新版本上傳)",
                            delete_after=30
                        )
                except Exception:
                    pass
                processed = True
            except Exception as e:
                await message.channel.send(f"❌ Error: {e} (發生錯誤)")

    if processed:
        try:
            await message.delete()
        except:
            pass

# Import commands to register them
from commands import delete, getcode, bind

delete.setup(bot)
getcode.setup(bot)
bind.setup(bot)

if __name__ == "__main__":
    bot.run(TOKEN)