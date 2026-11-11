# Module Odoo `cours_derives` (Odoo 17)

Forwards, options, portefeuille de dérivés, Markowitz, CAPM, volatilité (chapitre 2, GIIA ENSA Safi).

## Installation (Docker, comme dans le TP Odoo)
1. Dans le dossier du TP Odoo, copier ce dossier `cours_derives` dans `addons/`.
2. `docker compose up -d`, ouvrir http://localhost:8069, activer le **mode développeur**.
3. **Applications** → *Mettre à jour la liste des applications* → chercher « dérivés » → **Installer**.
4. Après une modification du code : `docker compose restart odoo`, puis *Applications → Mettre à jour* le module.

## Modèles
`cours.forward` (F0, arbitrage, Vt) · `cours.option` (payoff, profit, seuil, Black-Scholes) · `cours.portfolio` (valeur totale, payoff total, calls/puts) · `cours.markowitz` · `cours.capm` · `cours.volatility`.

## Vérification (Odoo 17.0, base de démonstration)
F0 = 81,62 € (gain d'arbitrage 0,38 €) · Vt = 9,98 € · portefeuille de démonstration : valeur 14,48 ; Markowitz 9,6 % / 14,42 % ; CAPM 10 %, alpha −2 % (surévalué).

## Limites
- Odoo 18 : remplacer la balise `<tree>` par `<list>` dans les vues XML.
- La prévision ML de la volatilité exige scikit-learn dans l'image Odoo ; sans lui, `vol_ml` reste à 0 (l'EWMA fonctionne sans dépendance).