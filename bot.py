import os
import json
import asyncio
from datetime import date, datetime
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
import aiohttp

# ---------- CONFIG ----------
# Set these in your environment variables (or replace with strings)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

NEWS_URL = "https://newsapi.org/v2/top-headlines"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

DATA_FILE = "reading_data.json"

# ---------- DATA HANDLING ----------
def load_reading_data() -> dict:
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_reading_data(data: dict):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_user_reading(user_id: str) -> dict:
    data = load_reading_data()
    today = str(date.today())
    user_data = data.get(user_id, {})
    if user_data.get("date") != today:
        # New day, reset progress
        user_data = {"date": today, "goal": 0, "read": 0}
        data[user_id] = user_data
        save_reading_data(data)
    return user_data

def update_reading(user_id: str, field: str, value: int):
    data = load_reading_data()
    user_data = get_user_reading(user_id)
    user_data[field] = value
    data[user_id] = user_data
    save_reading_data(data)

# ---------- BOT SETUP ----------
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# ---------- HELP COMMAND ----------
@bot.tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📚 Everyday Automation Bot - Help",
        description="Here are the things I can do for you:",
        color=0x3498db
    )
    embed.add_field(
        name="📰 `/news [query]`",
        value="Get latest 5 tech news headlines. Add an optional search term.",
        inline=False
    )
    embed.add_field(
        name="🌤️ `/weather <city>`",
        value="Current weather for a city (e.g., Tokyo, London).",
        inline=False
    )
    embed.add_field(
        name="📖 Reading Tracker",
        value=(
            "`/reading goal <pages>` - Set daily goal\n"
            "`/reading log <pages>` - Log pages read\n"
            "`/reading progress` - Show today's progress"
        ),
        inline=False
    )
    embed.add_field(
        name="⏰ `/studyreminder <minutes>`",
        value="Set a reminder that pings you after X minutes.",
        inline=False
    )
    embed.set_footer(text="Use /command to get started!")
    await interaction.response.send_message(embed=embed)

# ---------- NEWS COMMAND ----------
@bot.tree.command(name="news", description="Fetch latest tech news")
@app_commands.describe(query="Optional search keyword (e.g., AI, startups)")
async def news(interaction: discord.Interaction, query: Optional[str] = None):
    await interaction.response.defer()  # In case API is slow

    params = {
        "apiKey": NEWS_API_KEY,
        "category": "technology",
        "pageSize": 5,
        "country": "us"
    }
    if query:
        params["q"] = query  # Overrides category with search

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(NEWS_URL, params=params) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise Exception(f"NewsAPI error {resp.status}: {error_text}")
                data = await resp.json()

        if data.get("status") != "ok" or not data.get("articles"):
            await interaction.followup.send("❌ Could not fetch news. The API might be down or no articles found.")
            return

        articles = data["articles"][:5]
        embed = discord.Embed(
            title=f"📰 Latest Tech News {f'for \"{query}\"' if query else ''}",
            color=0xe74c3c
        )
        for i, article in enumerate(articles, 1):
            title = article.get("title", "No title")
            url = article.get("url", "")
            source = article.get("source", {}).get("name", "Unknown")
            # Truncate long titles
            if len(title) > 80:
                title = title[:77] + "..."
            embed.add_field(
                name=f"{i}. {title}",
                value=f"Source: {source} | [Read more]({url})",
                inline=False
            )
        embed.set_footer(text="Data from NewsAPI")
        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"⚠️ Something went wrong fetching news: {str(e)[:200]}")

# ---------- WEATHER COMMAND ----------
@bot.tree.command(name="weather", description="Get current weather for a city")
@app_commands.describe(city="City name (e.g., London)")
async def weather(interaction: discord.Interaction, city: str):
    await interaction.response.defer()

    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(WEATHER_URL, params=params) as resp:
                if resp.status == 404:
                    await interaction.followup.send(f"❌ City '{city}' not found. Please check spelling.")
                    return
                elif resp.status != 200:
                    raise Exception(f"OpenWeatherMap error {resp.status}")
                data = await resp.json()

        weather_desc = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        city_name = data["name"]

        embed = discord.Embed(
            title=f"🌤️ Weather in {city_name}",
            description=f"**{weather_desc}**",
            color=0x2ecc71
        )
        embed.add_field(name="Temperature", value=f"{temp}°C (feels like {feels_like}°C)", inline=True)
        embed.add_field(name="Humidity", value=f"{humidity}%", inline=True)
        embed.set_footer(text="Powered by OpenWeatherMap")
        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"⚠️ Weather fetch failed: {str(e)[:200]}")

# ---------- READING TRACKER GROUP ----------
reading_group = app_commands.Group(name="reading", description="Track your daily reading")

@reading_group.command(name="goal", description="Set your daily reading goal (pages)")
@app_commands.describe(pages="Number of pages you aim to read today")
async def reading_goal(interaction: discord.Interaction, pages: int):
    if pages <= 0:
        await interaction.response.send_message("❌ Please enter a positive number of pages.", ephemeral=True)
        return
    user_id = str(interaction.user.id)
    update_reading(user_id, "goal", pages)
    await interaction.response.send_message(f"✅ Daily goal set to **{pages} pages**. Good luck!")

@reading_group.command(name="log", description="Log pages you just read")
@app_commands.describe(pages="Number of pages read")
async def reading_log(interaction: discord.Interaction, pages: int):
    if pages <= 0:
        await interaction.response.send_message("❌ Please enter a positive number.", ephemeral=True)
        return
    user_id = str(interaction.user.id)
    user_data = get_user_reading(user_id)
    new_total = user_data["read"] + pages
    update_reading(user_id, "read", new_total)
    goal = user_data["goal"]
    if goal > 0:
        percent = min(100, int(new_total / goal * 100))
        progress_bar = ("🟩" * (percent // 10)) + ("⬜" * (10 - percent // 10))
        msg = f"📖 Logged {pages} pages. Total today: **{new_total}/{goal}**\n{progress_bar} {percent}%"
    else:
        msg = f"📖 Logged {pages} pages. Total today: **{new_total}** (no goal set)"
    await interaction.response.send_message(msg)

@reading_group.command(name="progress", description="Check today's reading progress")
async def reading_progress(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_data = get_user_reading(user_id)
    read = user_data["read"]
    goal = user_data["goal"]
    if goal == 0:
        await interaction.response.send_message("📊 No daily goal set. Use `/reading goal` first.")
    else:
        percent = min(100, int(read / goal * 100))
        progress_bar = ("🟩" * (percent // 10)) + ("⬜" * (10 - percent // 10))
        embed = discord.Embed(title="📚 Daily Reading Progress", color=0x9b59b6)
        embed.add_field(name="Read", value=f"{read} pages", inline=True)
        embed.add_field(name="Goal", value=f"{goal} pages", inline=True)
        embed.add_field(name="Progress", value=f"{progress_bar} {percent}%", inline=False)
        await interaction.response.send_message(embed=embed)

bot.tree.add_command(reading_group)

# ---------- STUDY REMINDER ----------
@bot.tree.command(name="studyreminder", description="Set a study reminder")
@app_commands.describe(minutes="Minutes until reminder")
async def studyreminder(interaction: discord.Interaction, minutes: int):
    if minutes <= 0:
        await interaction.response.send_message("❌ Please enter a positive number of minutes.", ephemeral=True)
        return
    await interaction.response.send_message(f"⏰ Reminder set! I'll ping you in **{minutes} minutes**.")
    await asyncio.sleep(minutes * 60)
    await interaction.followup.send(f"⏰ {interaction.user.mention} Time's up! Take a break or switch tasks. 🍅")

# ---------- RUN ----------
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise RuntimeError("Missing DISCORD_TOKEN environment variable")
    bot.run(DISCORD_TOKEN)