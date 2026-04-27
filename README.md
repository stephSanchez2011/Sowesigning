# 🤖 Bot SoWeSign Discord

Bot Discord pour gérer les liens de signature SoWeSign avec rappels automatiques.

## Fonctionnalités

- `/sowesign lien:[url]` — Enregistre et poste le lien dans `#signature` (période auto)
- `/sowesign lien:[url] periode:[Matin|Après-midi]` — Force la période
- `/lien` — Affiche les 5 derniers jours de liens
- `/aide` — Affiche l'aide
- Rappels automatiques à **9h00** et **14h00** (heure de Paris)

---

## 🚀 Déploiement

### 1. Créer le bot sur Discord Developer Portal

1. Va sur https://discord.com/developers/applications
2. **New Application** → donne un nom
3. Onglet **Bot** → **Add Bot**
4. Active **SERVER MEMBERS INTENT** et **MESSAGE CONTENT INTENT**
5. Copie le **Token**

### 2. Inviter le bot sur ton serveur

Dans **OAuth2 > URL Generator** :
- Scopes : `bot`, `applications.commands`
- Permissions : `Send Messages`, `Embed Links`, `View Channels`

Ouvre l'URL générée et invite le bot.

### 3. Créer le salon `#signature`

Crée un salon texte nommé exactement **`signature`** sur ton serveur Discord.

### 4. Pousser sur GitHub

```bash
git init
git add .
git commit -m "init bot sowesign"
git remote add origin https://github.com/TON_USERNAME/TON_REPO.git
git push -u origin main
```

### 5. Déployer sur Railway

1. Va sur https://railway.app
2. **New Project** → **Deploy from GitHub repo**
3. Sélectionne ton dépôt
4. Dans **Variables**, ajoute :
   ```
   DISCORD_TOKEN = ton_token_ici
   ```
5. Railway démarre automatiquement le bot ✅

---

## Structure des fichiers

```
sowesign-bot/
├── bot.py           # Code principal
├── requirements.txt # Dépendances Python
├── railway.toml     # Config Railway
├── nixpacks.toml    # Config Python 3.13
├── .gitignore
└── README.md
```

## Notes

- Les liens sont stockés localement dans `links.json` (Railway repart à zéro à chaque redéploiement — normal pour un usage quotidien)
- Les rappels utilisent le fuseau **Europe/Paris** (heure française, heure d'été incluse)
