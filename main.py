import discord, random, asyncio, json, os
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = ""
DATA_FILE = "restock_bot_data.json"
restock_channel_id = None
restock_active = False

FAKE_MESSAGES = [
    "🔥 **RESTOCK ALERT!** 10x Discount Accounts just got restocked! Go grab them fast!",
    "⚡ **NEW DROP!** 20x Premium Accounts added to the shop inventory!",
    "🎉 **RESTOCK!** 15x Nitro Boost accounts are now live and ready!",
    "💎 **HYPE DROP!** 50x Random Alt Accounts just hit the shelf!",
    "🚀 **RESTOCK ALERT!** 5x Streaming bundles just got restocked in the store!",
    "🌟 **FLASH RESTOCK!** 30x Cheap Accounts available right now!"
]

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({"restock_channel_id": restock_channel_id, "restock_active": restock_active}, f)

def load_data():
    global restock_channel_id, restock_active
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                d = json.load(f)
                restock_channel_id = d.get("restock_channel_id")
                restock_active = d.get("restock_active", False)
        except Exception as e: print(f"Error loading: {e}")

async def background_restock_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        if restock_active and restock_channel_id:
            ch = bot.get_channel(restock_channel_id) or await bot.fetch_channel(restock_channel_id)
            if ch:
                msg = random.choice(FAKE_MESSAGES)
                embed = discord.Embed(
                    title="📦 Automated Restock Notification",
                    description=msg,
                    color=discord.Color.from_rgb(0, 255, 127)
                )
                embed.set_footer(text="Shop Automation • Powered by Cipher")
                try:
                    await ch.send(embed=embed)
                except Exception as e: print(f"Send error: {e}")
        
        # Wait a random time between 10 seconds and 8 minutes (480 seconds)
        wait_time = random.randint(10, 480)
        await asyncio.sleep(wait_time)

@bot.event
async def on_ready():
    load_data()
    await bot.tree.sync()
    print(f"✨ Fake Restock Bot ready as {bot.user}!")
    if not background_restock_loop.is_running():
        bot.loop.create_task(background_restock_loop())

@bot.tree.command(name="setup-restock-channel", description="Set the channel where fake restocks will be sent.")
@app_commands.default_permissions(administrator=True)
async def setup_restock_channel(i: discord.Interaction, channel: discord.TextChannel):
    global restock_channel_id
    restock_channel_id = channel.id
    save_data()
    await i.response.send_message(f"✅ Restock feed channel set to {channel.mention}!", ephemeral=True)

@bot.tree.command(name="restock-on", description="Start the fake restock random loop.")
@app_commands.default_permissions(administrator=True)
async def restock_on(i: discord.Interaction):
    global restock_active
    restock_active = True
    save_data()
    await i.response.send_message("🟢 Fake restock loop is now **ENABLED** (Random drops between 10s & 8m).", ephemeral=True)

@bot.tree.command(name="restock-off", description="Stop the fake restock random loop.")
@app_commands.default_permissions(administrator=True)
async def restock_off(i: discord.Interaction):
    global restock_active
    restock_active = False
    save_data()
    await i.response.send_message("🔴 Fake restock loop is now **DISABLED**.", ephemeral=True)

bot.run(TOKEN)

