import discord
from discord.ext import tasks
import pytz
import os
from datetime import datetime, time

# ─── Configuration ───────────────────────────────────────────────────────────
TOKEN        = os.environ["DISCORD_TOKEN"]
CHANNEL_NAME = "signature"
TIMEZONE     = pytz.timezone("Europe/Paris")

MATIN_HEURE  = (9, 0)
APMIDI_HEURE = (14, 0)

# ─── Bot setup ───────────────────────────────────────────────────────────────
intents = discord.Intents.default()
bot = discord.Bot(intents=intents)

derniers_liens = {"matin": None, "aprem": None}

# ─── Helpers ─────────────────────────────────────────────────────────────────
def get_channel(guild):
    return discord.utils.get(guild.text_channels, name=CHANNEL_NAME)

def build_embed(lien: str, periode: str) -> discord.Embed:
    now      = datetime.now(TIMEZONE)
    emoji    = "🌅" if periode == "matin" else "🌆"
    label    = "du matin" if periode == "matin" else "de l'après-midi"
    embed    = discord.Embed(
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
        label = "9h00 — matin" if periode == "matin" else "14h00 — après-midi"
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
    ctx: discord.ApplicationContext,
    lien: discord.Option(str, "Le lien Sowesign du jour"),
    periode: discord.Option(str, "matin ou aprem (optionnel)", choices=["matin", "aprem"], required=False),
):
    if periode is None:
        periode = "matin" if datetime.now(TIMEZONE).hour < 12 else "aprem"

    await envoyer_signature(periode, lien)
    await ctx.respond("✅ Lien envoyé dans #signature !", ephemeral=True)

@bot.slash_command(name="lien", description="Affiche les derniers liens enregistrés")
async def afficher_lien(ctx: discord.ApplicationContext):
    m = derniers_liens["matin"] or "_aucun_"
    a = derniers_liens["aprem"] or "_aucun_"
    await ctx.respond(
        f"📋 **Derniers liens**\n🌅 Matin : {m}\n🌆 Après-midi : {a}",
        ephemeral=True,
    )

@bot.slash_command(name="aide", description="Affiche l'aide du bot")
async def aide(ctx: discord.ApplicationContext):
    embed = discord.Embed(title="📖 Aide — Bot Sowesign", color=0x5865F2)
    embed.add_field(name="/sowesign lien:[url]", value="Envoie le lien dans #signature. Période détectée automatiquement.", inline=False)
    embed.add_field(name="/sowesign lien:[url] periode:matin", value="Force matin ou aprem.", inline=False)
    embed.add_field(name="/lien", value="Affiche les derniers liens enregistrés.", inline=False)
    embed.set_footer(text="Rappels automatiques : 9h00 et 14h00 (Paris)")
    await ctx.respond(embed=embed, ephemeral=True)

# ─── Événements ──────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    rappel_auto.start()
    print(f"✅ Bot connecté : {bot.user} | {len(bot.guilds)} serveur(s)")

# ─── Lancement ───────────────────────────────────────────────────────────────
bot.run(TOKEN)
