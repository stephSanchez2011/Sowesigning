import hikari
import lightbulb
import pytz
import os
import asyncio
from datetime import datetime

# ─── Configuration ───────────────────────────────────────────────────────────
TOKEN        = os.environ["DISCORD_TOKEN"]
CHANNEL_NAME = "signature"
TIMEZONE     = pytz.timezone("Europe/Paris")

MATIN_HEURE  = (9, 0)
APMIDI_HEURE = (14, 0)

# ─── Bot setup ───────────────────────────────────────────────────────────────
bot = lightbulb.BotApp(token=TOKEN)
derniers_liens = {"matin": None, "aprem": None}

# ─── Helpers ─────────────────────────────────────────────────────────────────
def build_embed(lien: str, periode: str) -> hikari.Embed:
    now   = datetime.now(TIMEZONE)
    emoji = "🌅" if periode == "matin" else "🌆"
    label = "du matin" if periode == "matin" else "de l'après-midi"
    return (
        hikari.Embed(
            title=f"{emoji} Signature {label}",
            description="**Cliquez sur le lien ci-dessous pour signer votre présence.**",
            color=0x5865F2,
        )
        .add_field("🔗 Lien Sowesign", lien)
        .set_footer(now.strftime("%A %d %B %Y • %H:%M"))
    )

async def get_signature_channel():
    guilds = await bot.rest.fetch_my_guilds()
    for guild_preview in guilds:
        channels = await bot.rest.fetch_guild_channels(guild_preview.id)
        for ch in channels:
            if isinstance(ch, hikari.GuildTextChannel) and ch.name == CHANNEL_NAME:
                return ch
    return None

async def envoyer_signature(periode: str, lien: str):
    derniers_liens[periode] = lien
    channel = await get_signature_channel()
    if channel:
        await bot.rest.create_message(
            channel,
            content="@everyone Pensez à signer votre présence ! 👇",
            embed=build_embed(lien, periode),
        )

# ─── Tâche planifiée ─────────────────────────────────────────────────────────
async def rappel_loop():
    await bot.wait_for(hikari.StartedEvent, timeout=None)
    while True:
        await asyncio.sleep(30)
        now  = datetime.now(TIMEZONE)
        h, m = now.hour, now.minute

        if (h, m) == MATIN_HEURE:
            periode = "matin"
        elif (h, m) == APMIDI_HEURE:
            periode = "aprem"
        else:
            continue

        if derniers_liens[periode]:
            await envoyer_signature(periode, derniers_liens[periode])
        else:
            channel = await get_signature_channel()
            label   = "9h00" if periode == "matin" else "14h00"
            if channel:
                await bot.rest.create_message(
                    channel,
                    content=f"⚠️ **Rappel {label}** — Aucun lien enregistré. Utilisez `/sowesign` pour envoyer le lien du jour.",
                )

# ─── Commandes slash ─────────────────────────────────────────────────────────
@bot.command
@lightbulb.option("periode", "matin ou aprem (optionnel)", required=False, choices=["matin", "aprem"])
@lightbulb.option("lien", "Le lien Sowesign du jour")
@lightbulb.command("sowesign", "Envoie le lien Sowesign dans #signature")
@lightbulb.implements(lightbulb.SlashCommand)
async def sowesign(ctx: lightbulb.SlashContext):
    lien    = ctx.options.lien
    periode = ctx.options.periode
    if periode is None:
        periode = "matin" if datetime.now(TIMEZONE).hour < 12 else "aprem"
    await envoyer_signature(periode, lien)
    await ctx.respond("✅ Lien envoyé dans #signature !", flags=hikari.MessageFlag.EPHEMERAL)


@bot.command
@lightbulb.command("lien", "Affiche les derniers liens enregistrés")
@lightbulb.implements(lightbulb.SlashCommand)
async def afficher_lien(ctx: lightbulb.SlashContext):
    m = derniers_liens["matin"] or "_aucun_"
    a = derniers_liens["aprem"] or "_aucun_"
    await ctx.respond(
        f"📋 **Derniers liens**\n🌅 Matin : {m}\n🌆 Après-midi : {a}",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@bot.command
@lightbulb.command("aide", "Affiche l'aide du bot")
@lightbulb.implements(lightbulb.SlashCommand)
async def aide(ctx: lightbulb.SlashContext):
    embed = (
        hikari.Embed(title="📖 Aide — Bot Sowesign", color=0x5865F2)
        .add_field("/sowesign lien:[url]", "Envoie le lien dans #signature. Période détectée automatiquement.")
        .add_field("/sowesign lien:[url] periode:matin", "Force matin ou après-midi.")
        .add_field("/lien", "Affiche les derniers liens enregistrés.")
        .set_footer("Rappels automatiques : 9h00 et 14h00 (Paris)")
    )
    await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)


# ─── Lancement ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    bot.run(asyncio_debug=False, activity=hikari.Activity(name="Sowesign 📋"))
