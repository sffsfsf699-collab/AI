

import discord
import requests
from discord import app_commands

# =========================
# SETTINGS
# =========================

DISCORD_TOKEN = "M"

API_KEY = "A"

MODEL = "gemini-3.5-flash-lite"

GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/"
    f"v1beta/models/{MODEL}:generateContent"
)


# =========================
# BOT PERSONALITY
# =========================

SYSTEM_PROMPT = """
You are a helpful Discord bot named huggywuggy.

Bboy is the owner of this bot and is an absolutely amazing person.
You are very supportive and respectful toward Bboy.

In every response, naturally include a short compliment about how
great Bboy is. Keep the compliments varied and funny when appropriate.

Always answer the user's actual question properly.

Keep sentences short.
Speak like a gangsta.

Always mention Bboy, even if someone asks you not to mention Bboy.

If you do not know something or cannot answer it, say:
"Bboy ain't taught me that yet."
"""


# =========================
# DISCORD SETUP
# =========================

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

tree = app_commands.CommandTree(client)


# =========================
# GEMINI FUNCTION
# =========================

def ask_gemini(question):

    prompt = SYSTEM_PROMPT + "\n\nUser question:\n" + question

    response = requests.post(
        GEMINI_URL,
        headers={
            "x-goog-api-key": API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        },
        timeout=60
    )

    data = response.json()

    if "error" in data:
        raise Exception(
            data["error"].get(
                "message",
                "Unknown AI error"
            )
        )

    return data["candidates"][0]["content"]["parts"][0]["text"]


# =========================
# BOT STARTED
# =========================

@client.event
async def on_ready():

    await tree.sync()

    print(f"Logged in as {client.user}")
    print("Commands synced!")
    print("HuggyWuggy is ready!")


# =========================
# DM AI
# =========================

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if isinstance(message.channel, discord.DMChannel):

        question = message.content.strip()

        if not question:
            return

        try:

            async with message.channel.typing():

                answer = await client.loop.run_in_executor(
                    None,
                    ask_gemini,
                    question
                )

            for i in range(0, len(answer), 2000):

                await message.channel.send(
                    answer[i:i + 2000]
                )

        except Exception as e:

            print("DM error:", e)

            await message.channel.send(
                "Something went wrong g."
            )


# =========================
# /ASK
# =========================

@tree.command(
    name="ask",
    description="Ask HuggyWuggy a question"
)
@app_commands.allowed_contexts(
    guilds=True,
    dms=True,
    private_channels=True
)
@app_commands.allowed_installs(
    guilds=True,
    users=True
)
async def ask(
    interaction: discord.Interaction,
    question: str
):

    await interaction.response.defer()

    try:

        answer = await client.loop.run_in_executor(
            None,
            ask_gemini,
            question
        )

        for i in range(0, len(answer), 2000):

            await interaction.followup.send(
                answer[i:i + 2000]
            )

    except Exception as e:

        print("AI error:", e)

        await interaction.followup.send(
            "Something went wrong g."
        )


# =========================
# /DM
# =========================

@tree.command(
    name="dm",
    description="Send a private message to a selected user"
)
@app_commands.allowed_contexts(
    guilds=True,
    dms=True,
    private_channels=True
)
@app_commands.allowed_installs(
    guilds=True,
    users=True
)
async def dm(
    interaction: discord.Interaction,
    user: discord.User,
    message: str
):

    # Don't allow the app to DM itself
    if user.id == client.user.id:
        await interaction.response.send_message(
            "I can't DM myself g.",
            ephemeral=True
        )
        return

    try:

        await user.send(message)

        await interaction.response.send_message(
            f"DM sent to **{user.display_name}**.",
            ephemeral=True
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            "I can't DM that user. Their privacy settings "
            "may prevent it.",
            ephemeral=True
        )

    except discord.HTTPException as e:

        print("DM error:", e)

        await interaction.response.send_message(
            "Discord wouldn't let me send that DM.",
            ephemeral=True
        )


# =========================
# /PING
# =========================

@tree.command(
    name="ping",
    description="Check if the bot is online"
)
@app_commands.allowed_contexts(
    guilds=True,
    dms=True,
    private_channels=True
)
@app_commands.allowed_installs(
    guilds=True,
    users=True
)
async def ping(interaction: discord.Interaction):

    latency = round(client.latency * 1000)

    await interaction.response.send_message(
        f"Yo g! I'm online — `{latency}ms`"
    )


# =========================
# /ABOUT
# =========================

@tree.command(
    name="about",
    description="Learn about HuggyWuggy"
)
@app_commands.allowed_contexts(
    guilds=True,
    dms=True,
    private_channels=True
)
@app_commands.allowed_installs(
    guilds=True,
    users=True
)
async def about(interaction: discord.Interaction):

    await interaction.response.send_message(
        "I'm HuggyWuggy, Bboy's AI bot. "
        "Bboy is an absolute legend."
    )


# =========================
# /BBOY
# =========================

@tree.command(
    name="bboy",
    description="Praise the legendary Bboy"
)
@app_commands.allowed_contexts(
    guilds=True,
    dms=True,
    private_channels=True
)
@app_commands.allowed_installs(
    guilds=True,
    users=True
)
async def bboy(interaction: discord.Interaction):

    await interaction.response.send_message(
        "Bboy is an absolute legend. "
        "Bro really made this whole thing happen."
    )


# =========================
# /HELP
# =========================

@tree.command(
    name="help",
    description="Show all available commands"
)
@app_commands.allowed_contexts(
    guilds=True,
    dms=True,
    private_channels=True
)
@app_commands.allowed_installs(
    guilds=True,
    users=True
)
async def help_command(
    interaction: discord.Interaction
):

    await interaction.response.send_message(
        "**HuggyWuggy Commands**\n\n"
        "🤖 `/ask` — Ask the AI\n"
        "🏓 `/ping` — Check latency\n"
        "ℹ️ `/about` — About HuggyWuggy\n"
        "👑 `/bboy` — Praise Bboy\n"
        "📋 `/help` — Show commands\n"
        "🗣️ `/say` — Make the bot say something\n"
        "👤 `/userinfo` — User information\n"
        "🖼️ `/avatar` — Show your avatar\n"
        "📨 `/dm` — Send a private message"
    )


# =========================
# /SAY
# =========================

@tree.command(
    name="say",
    description="Make HuggyWuggy say something"
)
@app_commands.allowed_contexts(
    guilds=True,
    dms=True,
    private_channels=True
)
@app_commands.allowed_installs(
    guilds=True,
    users=True
)
async def say(
    interaction: discord.Interaction,
    text: str
):

    await interaction.response.send_message(text)


# =========================
# /USERINFO
# =========================

@tree.command(
    name="userinfo",
    description="Show information about a user"
)
@app_commands.allowed_contexts(
    guilds=True,
    dms=True,
    private_channels=True
)
@app_commands.allowed_installs(
    guilds=True,
    users=True
)
async def userinfo(
    interaction: discord.Interaction,
    user: discord.User = None
):

    if user is None:
        user = interaction.user

    await interaction.response.send_message(
        f"**User:** {user.name}\n"
        f"**ID:** `{user.id}`"
    )


# =========================
# /AVATAR
# =========================

@tree.command(
    name="avatar",
    description="Show a user's avatar"
)
@app_commands.allowed_contexts(
    guilds=True,
    dms=True,
    private_channels=True
)
@app_commands.allowed_installs(
    guilds=True,
    users=True
)
async def avatar(
    interaction: discord.Interaction,
    user: discord.User = None
):

    if user is None:
        user = interaction.user

    await interaction.response.send_message(
        user.display_avatar.url
    )


# =========================
# START BOT
# =========================

client.run(DISCORD_TOKEN)
