import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
from datetime import datetime, time
import pytz
import os

# ─── Configuration ───────────────────────────────────────────────────────────
TOKEN        = os.environ["DISCORD_TOKEN"]       # défini sur Railway
CHANNEL_NAME = "signature"                       # nom du channel cible
TIMEZONE     = pytz.timezone("Europe/Paris")

# Horaires d'envoi automatique (heure Paris)
MATIN_HEURE   = time(9, 0)   # 09:00
APMIDI_HEURE  = time(14, 0)  # 14:00

# ─── Bot setup ───────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Stocke le dernier lien envoyé (matin / après-midi)
derniers_liens = {"matin": None, "aprem": None}


# ─── Helpers ─────────────────────────────────────────────────────────────────
def get_channel(guild):
    return discord.utils.get(guild.text_channels, name=CHANNEL_NAME)


def build_embed(lien: str, periode: str) -> discord.Embed:
    heure_now = datetime.now(TIMEZONE).strftime("%H:%M")
    date_now  = datetime.now(TIMEZONE).strftime("%A %d %B %Y")

    emoji  = "🌅" if periode == "matin" else "🌆"
    label  = "du matin" if periode == "matin" else "de l'après-midi"
    titre  = f"{emoji} Signature {label}"

    embed = discord.Embed(
        title=titre,
        description=f"**Cliquez sur le lien ci-dessous pour signer votre présence.**",
        color=0x5865F2,
    )
    embed.add_field(name="🔗 Lien Sowesign", value=lien, inline=False)
    embed.set_footer(text=f"{date_now} • {heure_now}")
    return embed


async def envoyer_signature(periode: str, lien: str):
    for guild in bot.guilds:
        channel = get_channel(guild)
        if channel:
            embed = build_embed(lien, periode)
            await channel.send(
                content="@everyone Pensez à signer votre présence ! 👇",
                embed=embed,
            )
    derniers_liens[periode] = lien


# ─── Tâches planifiées ───────────────────────────────────────────────────────
@tasks.loop(minutes=1)
async def rappel_auto():
    now = datetime.now(TIMEZONE).time()

    if now.hour == MATIN_HEURE.hour and now.minute == MATIN_HEURE.minute:
        if derniers_liens["matin"]:
            await envoyer_signature("matin", derniers_liens["matin"])
        else:
            for guild in bot.guilds:
                channel = get_channel(guild)
                if channel:
                    await channel.send(
                        "⚠️ **Rappel 9h00** — Aucun lien Sowesign enregistré pour ce matin.\n"
                        "Utilisez `/sowesign lien:[url]` pour envoyer le lien du jour."
                    )

    elif now.hour == APMIDI_HEURE.hour and now.minute == APMIDI_HEURE.minute:
        if derniers_liens["aprem"]:
            await envoyer_signature("aprem", derniers_liens["aprem"])
        else:
            for guild in bot.guilds:
                channel = get_channel(guild)
                if channel:
                    await channel.send(
                        "⚠️ **Rappel 14h00** — Aucun lien Sowesign enregistré pour cet après-midi.\n"
                        "Utilisez `/sowesign lien:[url]` pour envoyer le lien du jour."
                    )


# ─── Commandes slash ─────────────────────────────────────────────────────────
@tree.command(name="sowesign", description="Envoie le lien Sowesign dans #signature")
@app_commands.describe(
    lien    = "Le lien Sowesign du jour",
    periode = "Matin ou après-midi (optionnel, détecté automatiquement)",
)
@app_commands.choices(periode=[
    app_commands.Choice(name="Matin",        value="matin"),
    app_commands.Choice(name="Après-midi",   value="aprem"),
])
async def sowesign(
    interaction: discord.Interaction,
    lien: str,
    periode: app_commands.Choice[str] = None,
):
    # Détection automatique si non précisé
    if periode is None:
        heure = datetime.now(TIMEZONE).hour
        val = "matin" if heure < 12 else "aprem"
    else:
        val = periode.value

    derniers_liens[val] = lien
    await envoyer_signature(val, lien)
    await interaction.response.send_message(
        f"✅ Lien envoyé dans <#{get_channel(interaction.guild).id}> !", ephemeral=True
    )


@tree.command(name="lien", description="Affiche le dernier lien Sowesign enregistré")
async def afficher_lien(interaction: discord.Interaction):
    m = derniers_liens["matin"] or "_aucun_"
    a = derniers_liens["aprem"] or "_aucun_"
    await interaction.response.send_message(
        f"📋 **Derniers liens enregistrés**\n🌅 Matin : {m}\n🌆 Après-midi : {a}",
        ephemeral=True,
    )


@tree.command(name="aide", description="Affiche l'aide du bot Sowesign")
async def aide(interaction: discord.Interaction):
    embed = discord.Embed(title="📖 Aide — Bot Sowesign", color=0x5865F2)
    embed.add_field(
        name="/sowesign lien:[url]",
        value="Envoie le lien dans #signature. La période (matin/après-midi) est détectée automatiquement.",
        inline=False,
    )
    embed.add_field(
        name="/sowesign lien:[url] periode:Matin",
        value="Force l'envoi pour le matin ou l'après-midi.",
        inline=False,
    )
    embed.add_field(name="/lien",  value="Affiche les derniers liens enregistrés.", inline=False)
    embed.add_field(name="/aide",  value="Affiche ce message.", inline=False)
    embed.set_footer(text="Rappels automatiques : 9h00 et 14h00 (heure de Paris)")
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ─── Événements ──────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    await tree.sync()
    rappel_auto.start()
    print(f"✅ Bot connecté en tant que {bot.user} | {len(bot.guilds)} serveur(s)")


# ─── Lancement ───────────────────────────────────────────────────────────────
bot.run(TOKEN)
