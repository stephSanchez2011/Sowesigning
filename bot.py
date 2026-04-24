import nextcord
from nextcord.ext import commands, tasks
import pytz
import os
from datetime import datetime

# ─── Configuration ───────────────────────────────────────────────────────────
TOKEN        = os.environ["DISCORD_TOKEN"]
CHANNEL_NAME = "signature"
TIMEZONE     = pytz.timezone("Europe/Paris")

MATIN_HEURE  = (9, 0)
APMIDI_HEURE = (14, 0)

# ─── Bot setup ───────────────────────────────────────────────────────────────
intents = nextcord.Intents.default()
bot = commands.Bot(intents=intents)

derniers_liens = {"matin": None, "aprem": None}

# ─── Helpers ─────────────────────────────────────────────────────────────────
def get_channel(guild):
    return nextcord.utils.get(guild.text_channels, name=CHANNEL_NAME)

def build_embed(lien: str, periode: str) -> nextcord.Embed:
    now   = datetime.now(TIMEZONE)
    emoji = "🌅" if periode == "matin" else "🌆"
    label = "du matin" if periode == "matin" else "de l'après-midi"
    embed = nextcord.Embed(
        title=f"{emoji} Signature {label}",
        description="**Cliquez sur le lien ci-dessous pour signer votre présence.**",
        color=0x5865F2,
    )
    embed.add_field(name="🔗 Lien Sowesign", value=lien, inline=False)
    embed.set_footer(text=now.strftime("%A %d %B %Y • %H:%M"))
    return embed

async def envoyer_signature(periode: str, lien: str):
    derniers_liens[periode] = lien
    for guild in bot.guilds:
        channel = get_channel(guild)
        if channel:
            await channel.send(
                content="@everyone Pensez à signer votre présence ! 👇",
                embed=build_embed(lien, periode),
            )

# ─── Tâche planifiée ─────────────────────────────────────────────────────────
@tasks.loop(minutes=1)
async def rappel_auto():
    now  = datetime.now(TIMEZONE)
    h, m = now.hour, now.minute

    if (h, m) == MATIN_HEURE:
        periode = "matin"
    elif (h, m) == APMIDI_HEURE:
        periode = "aprem"
    else:
        return

    if derniers_liens[periode]:
        await envoyer_signature(periode, derniers_liens[periode])
    else:
        label = "9h00" if periode == "matin" else "14h00"
        for guild in bot.guilds:
            channel = get_channel(guild)
            if channel:
                await channel.send(
                    f"⚠️ **Rappel {label}** — Aucun lien enregistré.\n"
                    f"Utilisez `/sowesign` pour envoyer le lien du jour."
                )

# ─── Commandes slash ─────────────────────────────────────────────────────────
@bot.slash_command(name="sowesign", description="Envoie le lien Sowesign dans #signature")
async def sowesign(
    interaction: nextcord.Interaction,
    lien: str = nextcord.SlashOption(name="lien", description="Le lien Sowesign du jour"),
    periode: str = nextcord.SlashOption(
        name="periode",
        description="matin ou aprem (optionnel, détecté automatiquement)",
        choices={"Matin": "matin", "Après-midi": "aprem"},
        required=False,
    ),
):
    if periode is None:
        periode = "matin" if datetime.now(TIMEZONE).hour < 12 else "aprem"

    await envoyer_signature(periode, lien)
    await interaction.response.send_message("✅ Lien envoyé dans #signature !", ephemeral=True)


@bot.slash_command(name="lien", description="Affiche les derniers liens enregistrés")
async def afficher_lien(interaction: nextcord.Interaction):
    m = derniers_liens["matin"] or "_aucun_"
    a = derniers_liens["aprem"] or "_aucun_"
    await interaction.response.send_message(
        f"📋 **Derniers liens**\n🌅 Matin : {m}\n🌆 Après-midi : {a}",
        ephemeral=True,
    )


@bot.slash_command(name="aide", description="Affiche l'aide du bot")
async def aide(interaction: nextcord.Interaction):
    embed = nextcord.Embed(title="📖 Aide — Bot Sowesign", color=0x5865F2)
    embed.add_field(name="/sowesign lien:[url]", value="Envoie le lien dans #signature. Période détectée automatiquement.", inline=False)
    embed.add_field(name="/sowesign lien:[url] periode:Matin", value="Force matin ou après-midi.", inline=False)
    embed.add_field(name="/lien", value="Affiche les derniers liens enregistrés.", inline=False)
    embed.set_footer(text="Rappels automatiques : 9h00 et 14h00 (Paris)")
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ─── Événements ──────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    rappel_auto.start()
    print(f"✅ Bot connecté : {bot.user} | {len(bot.guilds)} serveur(s)")


# ─── Lancement ───────────────────────────────────────────────────────────────
bot.run(TOKEN)
