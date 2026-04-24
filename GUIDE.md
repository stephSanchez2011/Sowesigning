# 🤖 Bot Discord Sowesign — Guide d'installation

## Ce que vous aurez à la fin
Un bot Discord qui envoie automatiquement le lien Sowesign dans `#signature` chaque matin (9h) et après-midi (14h), avec un rappel à votre demande via la commande `/sowesign`.

---

## Étape 1 — Créer le bot sur Discord

1. Allez sur https://discord.com/developers/applications
2. Cliquez **New Application** → donnez un nom (ex: `SowesignBot`)
3. Dans le menu gauche, cliquez **Bot**
4. Cliquez **Reset Token** → copiez le token (gardez-le secret !)
5. Dans la section **Privileged Gateway Intents**, activez :
   - **Message Content Intent**
6. Dans le menu gauche, cliquez **OAuth2 → URL Generator**
   - Cochez **bot** et **applications.commands**
   - Dans Bot Permissions, cochez : **Send Messages**, **Embed Links**, **Mention Everyone**
   - Copiez l'URL générée et ouvrez-la dans votre navigateur pour inviter le bot sur votre serveur

---

## Étape 2 — Mettre le code sur GitHub

1. Créez un compte sur https://github.com (si ce n'est pas déjà fait)
2. Créez un nouveau dépôt (bouton **+** → **New repository**)
   - Nom : `sowesign-bot`
   - Visibilité : **Private** (recommandé)
3. Sur votre ordinateur, créez un dossier `sowesign-bot/` avec ces 3 fichiers :
   - `bot.py`
   - `requirements.txt`
   - `Procfile`
4. Uploadez les fichiers sur GitHub (bouton **Add file → Upload files**)

---

## Étape 3 — Déployer sur Railway

1. Allez sur https://railway.app et créez un compte (connexion avec GitHub)
2. Cliquez **New Project → Deploy from GitHub repo**
3. Sélectionnez votre dépôt `sowesign-bot`
4. Une fois le projet créé, cliquez sur votre service → onglet **Variables**
5. Ajoutez la variable d'environnement :
   - Clé : `DISCORD_TOKEN`
   - Valeur : *votre token copié à l'étape 1*
6. Railway va démarrer le bot automatiquement. C'est tout ! 🎉

---

## Utilisation au quotidien

### Envoyer le lien Sowesign

Dans n'importe quel channel Discord, tapez :

```
/sowesign lien:https://votre-lien-sowesign.fr
```

Le bot détecte automatiquement si c'est le matin ou l'après-midi.

Pour forcer la période :
```
/sowesign lien:https://... periode:Matin
/sowesign lien:https://... periode:Après-midi
```

### Autres commandes

| Commande | Description |
|---|---|
| `/sowesign lien:[url]` | Envoie le lien dans #signature |
| `/lien` | Affiche les derniers liens enregistrés |
| `/aide` | Affiche l'aide |

### Rappels automatiques

Le bot envoie un message dans `#signature` chaque jour à :
- **9h00** (heure de Paris) — si un lien matin a été enregistré
- **14h00** (heure de Paris) — si un lien après-midi a été enregistré

Si aucun lien n'a été donné, le bot envoie un rappel pour vous demander de le fournir.

---

## En cas de problème

- **Le bot ne répond pas** → vérifiez que le token est bien renseigné dans Railway
- **Le bot ne trouve pas #signature** → vérifiez que le channel s'appelle exactement `signature` (sans le `#`)
- **Les commandes slash n'apparaissent pas** → attendez 1 minute après le démarrage du bot

---

*Bot développé pour une utilisation en formation professionnelle.*
