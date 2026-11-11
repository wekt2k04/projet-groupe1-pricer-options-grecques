# Le travail de la semaine : méthode

Tout le travail du projet est préparé à l'avance sur des branches `prep/s2` à `prep/s7` (une par semaine, chacune contient les précédentes). **Ces branches ne sont jamais fusionnées.** Chaque semaine :

1. Ouvrir la fiche de la semaine : `docs/semaines/S<n>.md` **sur la branche `prep/s<n>`** (sur GitHub : choisir la branche dans le menu, puis ouvrir le fichier). Elle dit qui prend quels fichiers, avec quelles commandes, et ce qu'il faut comprendre.
2. Récupérer **ses** fichiers dans **sa** branche, partie de `main` :
   ```bash
   git fetch origin
   git checkout -b <prenom>-s<n> origin/main
   git checkout origin/prep/s<n> -- <fichiers indiqués dans la fiche>
   ```
3. Exécuter chez soi (notebook avec Internet, Odoo sous Docker, tests), lire la partie « À comprendre ».
4. Commiter **à son nom** : `git commit -m "[Prénom] <verbe + objet> (<étape>)"`, `git push -u origin <prenom>-s<n>`, ouvrir la PR, la faire relire par un autre membre, fusionner après approbation.

Calendrier : S2 notebooks Python · S3 extension Odoo · S4 vues, LSTM, rotation · S5 bouton Odoo → IA · S6 rapport · S7 soutenance.
