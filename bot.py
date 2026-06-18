import os
import aiohttp
import discord
from discord.ext import tasks
from dotenv import load_dotenv
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TWITCH_CHANNEL = os.getenv("TWITCH_CHANNEL", "generaleddy")

MESSAGE_ID_FILE = "message_id.txt"
UK_TZ = ZoneInfo("Europe/London")

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# ── Persistence ───────────────────────────────────────────────────────────────

def load_message_id():
    if os.path.exists(MESSAGE_ID_FILE):
        with open(MESSAGE_ID_FILE) as f:
            text = f.read().strip()
            return int(text) if text else None
    return None


def save_message_id(message_id):
    with open(MESSAGE_ID_FILE, "w") as f:
        f.write(str(message_id))


# ── Twitch API ────────────────────────────────────────────────────────────────

async def twitch_get(token, url):
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {token}",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            return await resp.json()


async def get_twitch_token():
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials",
    }
    async with aiohttp.ClientSession() as session:
        async with session.post("https://id.twitch.tv/oauth2/token", params=params) as resp:
            return (await resp.json())["access_token"]


async def get_schedule():
    token = await get_twitch_token()
    user = (await twitch_get(token, f"https://api.twitch.tv/helix/users?login={TWITCH_CHANNEL}"))["data"][0]
    broadcaster_id = user["id"]

    schedule = await twitch_get(token, f"https://api.twitch.tv/helix/schedule?broadcaster_id={broadcaster_id}&first=7")
    streams = (await twitch_get(token, f"https://api.twitch.tv/helix/streams?user_id={broadcaster_id}"))["data"]
    live = streams[0] if streams else None

    return schedule, live, user.get("profile_image_url")


# ── Helpers ───────────────────────────────────────────────────────────────────

def to_ts(start_time):
    return int(datetime.fromisoformat(start_time.replace("Z", "+00:00")).timestamp())


# ── Discord updates ───────────────────────────────────────────────────────────

async def update_channel_topic(channel, live, segments):
    if live:
        topic = "🔴 LIVE NOW • twitch.tv/generaleddy"
    elif segments:
        title = segments[0].get("title") or "Next stream"
        dt = datetime.fromisoformat(segments[0]["start_time"].replace("Z", "+00:00")).astimezone(UK_TZ)
        topic = f"🚀 Next Stream: {title} • {dt.strftime('%a %d %b %H:%M %Z')}"
    else:
        topic = "📅 Stream schedule synced from Twitch"

    if channel.topic != topic:
        await channel.edit(topic=topic)


def build_embed(schedule_data, live, avatar_url):
    segments = schedule_data.get("data", {}).get("segments", [])
    status = "🔴 LIVE" if live else "⚫ OFFLINE"

    embed = discord.Embed(
        title=f"🛰️ twitch.tv/generaleddy  {status}",
        url=f"https://www.twitch.tv/{TWITCH_CHANNEL}",
        color=0xFF0000 if live else 0x9146FF,
    )
    if avatar_url:
        embed.set_thumbnail(url=avatar_url)

    if not segments:
        embed.add_field(
            name="No streams scheduled",
            value=f"Check [Twitch](https://www.twitch.tv/{TWITCH_CHANNEL}/schedule) for updates.",
            inline=False,
        )
    else:
        next_stream = segments[0]
        title = next_stream.get("title") or "Untitled stream"
        category = (next_stream.get("category") or {}).get("name", "No category")
        ts = to_ts(next_stream["start_time"])

        embed.add_field(
            name="🚀 NEXT STREAM",
            value=f"🎮 **{title}**\n{category}\n\n🕒 <t:{ts}:F>\n⏳ <t:{ts}:R>",
            inline=False,
        )

        upcoming = [
            f"• **{s.get('title') or 'Untitled stream'}**\n  <t:{to_ts(s['start_time'])}:f>"
            for s in segments[1:7]
        ]
        if upcoming:
            embed.add_field(
                name="📋 UPCOMING STREAMS",
                value="\n\n".join(upcoming),
                inline=False,
            )

    now_ts = int(datetime.now(timezone.utc).timestamp())
    embed.add_field(name="", value=f"Last synced: <t:{now_ts}:R>", inline=False)
    embed.set_footer(text="Synced from Twitch")
    return embed


# ── Bot loop ──────────────────────────────────────────────────────────────────

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    update_schedule.start()


@tasks.loop(minutes=30)
async def update_schedule():
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"ERROR: Could not find channel {CHANNEL_ID}.")
        return

    try:
        schedule_data, live, avatar_url = await get_schedule()
    except Exception as e:
        print(f"ERROR fetching Twitch data: {e}")
        return

    segments = schedule_data.get("data", {}).get("segments", [])
    embed = build_embed(schedule_data, live, avatar_url)

    try:
        await update_channel_topic(channel, live, segments)
    except Exception as e:
        print(f"ERROR updating channel topic: {e}")

    message_id = load_message_id()
    if message_id:
        try:
            message = await channel.fetch_message(message_id)
            await message.edit(embed=embed)
            print(f"Updated embed at {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
            return
        except discord.NotFound:
            print("Pinned message not found — posting a new one.")

    message = await channel.send(embed=embed)
    save_message_id(message.id)
    await message.pin()
    print(f"Posted and pinned new embed (id={message.id})")


client.run(DISCORD_TOKEN)
