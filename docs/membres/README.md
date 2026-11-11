# Premier commit de chaque membre (S1)

Le guide note la discipline Git : **au moins un commit par semaine et par membre, avec son prénom dans le message**. Un nom absent de l'historique fait passer la note de collective à individuelle. Ce dossier sert à faire ce premier commit en 2 minutes.

## Ce qu'il faut faire

Créer **ton** fichier `docs/membres/<prenom>.md` (exemple : `docs/membres/hiba.md`) en recopiant le modèle ci-dessous et en le complétant. Chacun écrit dans son propre fichier, donc personne n'entre en conflit avec les autres.

### Option A, sans rien installer : depuis le site GitHub

1. Accepter l'invitation au dépôt (e-mail de GitHub ou https://github.com/notifications).
2. Ouvrir le dépôt, aller dans `docs/membres/`, cliquer sur **Add file › Create new file**.
3. Nom du fichier : `<prenom>.md`. Coller le modèle et le compléter.
4. Message de commit : `[Prénom] Ajout de ma fiche membre`. Choisir **Commit directly to the main branch**, puis valider.

### Option B : avec Git (si tu as déjà cloné le dépôt)

```bash
git clone https://github.com/wekt2k04/projet-groupe1-pricer-options-grecques.git
cd projet-groupe1-pricer-options-grecques
# créer docs/membres/<prenom>.md avec le modèle ci-dessous
git add docs/membres/<prenom>.md
git commit -m "[Prénom] Ajout de ma fiche membre"
git push
```

## Modèle

```markdown
# <Prénom NOM> (<filière>)

- GitHub : <identifiant>
- Rôle S1 à S4 : <rôle proposé dans le README, ou celui convenu en séance>
- Rôle S5 à S7 : <rôle après la rotation>
- Ce que je fais en S2 (une phrase) : <...>
- Une notion du projet que je sais déjà expliquer (une phrase) : <...>
```
