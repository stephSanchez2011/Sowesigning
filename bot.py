import discord
from discord import app_commands
from discord.ext import commands, tasks
import json
import os
from datetime import datetime
import pytz
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PARIS_TZ = pytz.timezone("Europe/Paris")
DATA_FILE = "links.json"
SIGNATURE_CHANNEL_NAME = "signature"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_data(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_periode_auto() -> str:
    now = datetime.now(PARIS_TZ)
    return "Matin" if now.hour < 13 else "Après-midi"


def get_today_key() -> str:
    return datetime.now(PARIS_TZ).strftime("%Y-%m-%d")


def get_signature_channel(guild: discord.Guild) -> discord.TextChannel | None:
    for channel in guild.text_channels:
        if channel.name == SIGNATURE_CHANNEL_NAME:
            return channel
    return None


@bot.event
async def on_ready():
    logger.info(f"Bot connecté : {bot.user} (ID: {bot.user.id})")
    try:
        synced = await tree.sync()
        logger.info(f"{len(synced)} commande(s) synchronisée(s)")
    except Exception as e:
        logger.error(f"Erreur de synchronisation : {e}")
    rappel_matin.start()
    rappel_aprem.start()


# ─── /sowesign ────────────────────────────────────────────────────────────────

class PeriodeChoice(discord.Enum):
    Matin = "Matin"
    Apres_midi = "Après-midi"


@tree.command(name="sowesign", description="Enregistre un lien SoWeSign dans #signature")
@app_commands.describe(
    lien="Le lien SoWeSign à envoyer",
    periode="Forcer Matin ou Après-midi (facultatif, détection auto sinon)"
)
@app_commands.choices(periode=[
    app_commands.Choice(name="Matin", value="Matin"),
    app_commands.Choice(name="Après-midi", value="Après-midi"),
])
async def sowesign(
    interaction: discord.Interaction,
    lien: str,
    periode: str | None = None,
):
    if not lien.startswith("http"):
        await interaction.response.send_message(
            "❌ Le lien doit commencer par `http://` ou `https://`.", ephemeral=True
        )
        return

    periode_finale = periode if periode else get_periode_auto()
    today = get_today_key()

    data = load_data()
    guild_id = str(interaction.guild_id)
    if guild_id not in data:
        data[guild_id] = {}
    if today not in data[guild_id]:
        data[guild_id][today] = {}

    data[guild_id][today][periode_finale] = {
        "lien": lien,
        "auteur": str(interaction.user),
        "timestamp": datetime.now(PARIS_TZ).isoformat(),
    }
    save_data(data)

    # Envoyer dans #signature
    channel = get_signature_channel(interaction.guild)
    embed = discord.Embed(
        title=f"📋 SoWeSign — {periode_finale}",
        description=f"[Cliquez ici pour signer]({lien})",
        color=0x5865F2 if periode_finale == "Matin" else 0xEB459E,
        timestamp=datetime.now(PARIS_TZ),
    )
    embed.set_footer(text=f"Ajouté par {interaction.user.display_name}")

    if channel:
        await channel.send(embed=embed)
        await interaction.response.send_message(
            f"✅ Lien **{periode_finale}** enregistré et envoyé dans {channel.mention} !",
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(
            f"✅ Lien **{periode_finale}** enregistré, mais je n'ai pas trouvé le salon `#signature`.",
            ephemeral=True,
        )


# ─── /lien ────────────────────────────────────────────────────────────────────

@tree.command(name="lien", description="Affiche les derniers liens SoWeSign enregistrés")
async def lien(interaction: discord.Interaction):
    data = load_data()
    guild_id = str(interaction.guild_id)
    today = get_today_key()

    guild_data = data.get(guild_id, {})
    today_data = guild_data.get(today, {})

    # Récupérer les 5 derniers jours
    all_days = sorted(guild_data.keys(), reverse=True)[:5]

    embed = discord.Embed(
        title="📎 Derniers liens SoWeSign",
        color=0x57F287,
    )

    if not all_days:
        embed.description = "Aucun lien enregistré pour ce serveur."
    else:
        for day in all_days:
            day_data = guild_data[day]
            lines = []
            for p in ["Matin", "Après-midi"]:
                if p in day_data:
                    info = day_data[p]
                    lines.append(f"**{p}** : [Lien]({info['lien']}) — par {info['auteur']}")
            if lines:
                label = "📅 Aujourd'hui" if day == today else f"📅 {day}"
                embed.add_field(name=label, value="\n".join(lines), inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)


# ─── /aide ────────────────────────────────────────────────────────────────────

@tree.command(name="aide", description="Affiche l'aide du bot SoWeSign")
async def aide(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Aide — Bot SoWeSign",
        color=0xFEE75C,
    )
    embed.add_field(
        name="/sowesign lien:[url]",
        value="Enregistre et envoie le lien dans `#signature`.\nLa période (Matin/Après-midi) est détectée automatiquement.",
        inline=False,
    )
    embed.add_field(
        name="/sowesign lien:[url] periode:[Matin|Après-midi]",
        value="Force la période manuellement.",
        inline=False,
    )
    embed.add_field(
        name="/lien",
        value="Affiche les 5 derniers jours de liens enregistrés.",
        inline=False,
    )
    embed.add_field(
        name="/aide",
        value="Affiche ce message d'aide.",
        inline=False,
    )
    embed.add_field(
        name="⏰ Rappels automatiques",
        value=(
            "• **9h00** (Paris) — rappel lien Matin\n"
            "• **14h00** (Paris) — rappel lien Après-midi"
        ),
        inline=False,
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ─── Rappels automatiques ─────────────────────────────────────────────────────

async def send_rappel(periode: str):
    data = load_data()
    today = get_today_key()
    now_str = datetime.now(PARIS_TZ).strftime("%H:%M")

    for guild in bot.guilds:
        guild_id = str(guild.id)
        channel = get_signature_channel(guild)
        if not channel:
            continue

        lien_info = data.get(guild_id, {}).get(today, {}).get(periode)

        if lien_info:
            embed = discord.Embed(
                title=f"⏰ Rappel SoWeSign — {periode}",
                description=f"[Cliquez ici pour signer]({lien_info['lien']})",
                color=0x5865F2 if periode == "Matin" else 0xEB459E,
                timestamp=datetime.now(PARIS_TZ),
            )
            embed.set_footer(text=f"Lien fourni par {lien_info['auteur']}")
            await channel.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f"⚠️ Aucun lien SoWeSign — {periode}",
                description=(
                    f"Il est **{now_str}** et aucun lien **{periode}** n'a encore été partagé aujourd'hui.\n"
                    f"Utilisez `/sowesign lien:[votre-lien]` pour en ajouter un !"
                ),
                color=0xED4245,
            )
            await channel.send(embed=embed)


@tasks.loop(time=datetime.now(PARIS_TZ).replace(hour=9, minute=0, second=0, microsecond=0).timetz())
async def rappel_matin():
    await send_rappel("Matin")


@tasks.loop(time=datetime.now(PARIS_TZ).replace(hour=14, minute=0, second=0, microsecond=0).timetz())
async def rappel_aprem():
    await send_rappel("Après-midi")


# ─── Lancement ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise ValueError("La variable d'environnement DISCORD_TOKEN est manquante !")
    bot.run(token)
