# CLAUDE.md — Groupe 1, Projet 1 « Pricer d'Options & Grecques »

Fichier de pilotage du projet : ce qui est fait, ce qui reste à faire, qui le fait, avec quelles commandes et quelle preuve. Il est mis à jour à chaque jalon (§12) et sert deux lecteurs :

| Tu es… | Lis dans cet ordre |
|---|---|
| **Membre du groupe** qui ouvre le dépôt | §14 « Guide du membre » (installation, règles notées, ta tâche, façon de contribuer), puis l'étape de §9 qui te concerne |
| **Une session Claude** (Claude Code ou tout assistant qui lit ce fichier), quel que soit le membre qui la lance | §0 en entier, puis §11 (règles, dont celles qui dépendent de l'utilisateur de la session) |

## 0. Reprise d'une session Claude en 6 gestes

0. Identifier l'utilisateur de la session (lui demander son prénom s'il ne l'a pas donné) : identité Git, attribution et accord avant de pousser en dépendent (§11).
1. Lire ce fichier, puis `docs/COMPRENDRE.md` (explications destinées à l'équipe).
2. Lancer `pytest` à la racine : **25 tests, tous verts** attendus (20 dans `tests/test_pricing.py`, 5 dans `tests/test_data.py`). Sinon, corriger avant tout le reste.
3. Lire §8 (état) et §9 (plan en étapes atomiques) ; reprendre à la première case non cochée de §9.
4. Réclamer les bloquants de §9.0 à leur détenteur (colonne « Détenu par »).
5. Avant de terminer : procédure P6 de §9.9 (mettre à jour §8, §9, §12).

**Vocabulaire.** `[x]` : fait **et** prouvé (commande ou fichier cité) ; `[ ]` : à faire ; « proposé » : choix de Claude non validé par le groupe ; « à trancher » : choix ouvert, avec un défaut écrit ; « défaut appliqué » : défaut retenu faute de réponse, consigné en §5 ; « non vérifié » : écrit mais jamais exécuté.

**Sources de vérité, par ordre de priorité** : tests (`tests/`) > `CONVENTIONS.md` > ce fichier > `README.md` > `docs/`. Une contradiction se corrige dans le fichier de rang inférieur.

**Si l'utilisateur de la session est injoignable** : appliquer le défaut écrit, le consigner en §5, continuer. Jamais sans son accord explicite : pousser, fusionner, écrire le nom d'un autre étudiant, contacter un autre groupe ou le professeur.

## 1. Contexte

- **Équipe** : 5 membres ; noms et rôles dans le README, chacun remplit sa ligne. **Wilfried** (IDIA3, dernière année du cycle ingénieur à l'ENSA Safi) est propriétaire du dépôt et a construit le lot S1 avec Claude ; dans ses sessions, il attend du français, des réponses concises, denses et tranchées. N'importe quel membre peut lancer une session Claude sur ce dépôt (§11).
- **Module** : Finance des Marchés et ERP, 2026-2027, enseignant Pr Abdelilah JRAIFI. Le « guide » est le PDF `Guide_Complet_Projets_Fin&marchés-ERP_26.pdf` (30 pages, sur le Drive du professeur ; le connecteur Drive de Claude n'y accède pas, compte différent). Son contenu utile est résumé ici.
- **Groupe 1** : 5 étudiants d'après l'annexe C du guide (3 IDIA3, 2 GINF3). L'en-tête du Projet 1 dans le corps du guide n'en liste que 4 : Wilfried est le cinquième, absent de cet en-tête. Le guide ne définit des rôles que pour 3 et 4 personnes (G1 figure dans la liste des groupes de 4).
- **Calendrier** : message du professeur : un mini-compte rendu par semaine, remis au début de chaque séance, **à partir de la séance du 11 novembre 2026** ; présence obligatoire de tous ; retards non acceptés ; le dossier Drive contient le sujet, la boîte à outils et le modèle de mini-compte rendu hebdomadaire. Les dates S1 à S7 du Gantt (11/11, 18/11, 25/11, 02/12, 09/12, 16/12, 23/12) supposent une séance hebdomadaire : **indicatif**. Le 18/11 est férié au Maroc : séance S2 probablement déplacée, à confirmer.
- **Dépôt GitHub** : `https://github.com/wekt2k04/projet-groupe1-pricer-options-grecques` (privé, compte de Wilfried, branche par défaut `main`).
- **Nous sommes le 10/11/2026 au soir** quand ce fichier est rédigé ; la séance S1 est le lendemain.

## 2. Objectif du projet (spécification du guide)

Construire un outil complet qui valorise une option européenne avec Black-Scholes, calcule les cinq Grecques, les expose dans Odoo en étendant `cours.option` du module `cours_derives` (TP 0), et utilise un LSTM pour prédire la volatilité du lendemain. C'est le projet **« socle »** : les groupes 4, 5, 6, 7 et 9 réutilisent `bs_price` et `greeks`.

| Rubrique | Contenu imposé |
|---|---|
| Théorie | EDP de Black-Scholes ; `d1 = [ln(S/K) + (r + σ²/2)T]/(σ√T)`, `d2 = d1 − σ√T` ; Call = `S·N(d1) − K·e^(−rT)·N(d2)`, Put = `K·e^(−rT)·N(−d2) − S·N(−d1)` ; Delta = `N(d1)`, Gamma = `φ(d1)/(Sσ√T)`, Vega = `Sφ(d1)√T`, Theta_call = `−Sφ(d1)σ/(2√T) − rKe^(−rT)N(d2)`, Rho_call = `KTe^(−rT)N(d2)` ; parité `C − P = S − Ke^(−rT)` |
| Hypothèses | sous-jacent log-normal, σ et r constants ; pas de dividendes ni de coûts ; vente à découvert autorisée ; marché continu sans arbitrage ; option européenne |
| Données | prix d'une action (ex. AAPL) via yfinance sur 1 à 2 ans (clôture ajustée) ; rendements log `r_t = ln(S_t/S_{t−1})` ; volatilité historique annualisée `σ = std(r_t) × √252` |
| Python | `d1`, `d2` avec NumPy ; `scipy.stats.norm.cdf/pdf` ; `bs_price(S, K, T, r, sigma, type)` et `greeks(...)` qui renvoie `{delta, gamma, vega, theta, rho}` ; validation par différences finies `(V(S+h) − V(S−h))/2h` ; parité dans les tests pytest |
| Odoo | `_inherit = 'cours.option'` ; champs `greeks_delta…greeks_rho` (ainsi que volatilité et prix si absents) ; champs calculés `@api.depends('spot','strike','maturite','taux','volatilite','type')` appelant `greeks()` ; bouton « Calculer » (`action_calculer()`) ; vues formulaire (groupes « Paramètres » et « Résultats / Grecques »), liste, graphique (évolution du Delta en fonction du spot) |
| IA | cible : volatilité de demain à partir des 30 derniers jours (LSTM, Keras) ; variante : volatilité implicite future via ARIMA ou LSTM ; données : volatilité réalisée glissante (ex. 5 jours), fenêtres de 30 valeurs, cible = valeur du jour suivant ; MinMaxScaler appris sur le train seul ; découpage chronologique 70 / 15 / 15, jamais aléatoire |

Mots-clés du guide : Black-Scholes · Grecques · volatilité historique · LSTM · extension de cours.option.

## 3. Cadre imposé par le guide (tous groupes)

- **Phases** : 0 fiche de lecture → 1 théorie / données → 2 Python → 3 Odoo → 4 IA. 10 groupes, 7 semaines.
- **Stack** : Odoo 17 Community (Docker) + PostgreSQL ; Python 3 ; NumPy, SciPy, pandas ; scikit-learn / Keras / PyTorch ; yfinance ; pytest ; GitHub.
- **Calendrier et attendus du mini-compte rendu** (10 minutes, un membre différent chaque semaine, appuyé sur le Gantt à jour) :

| Sem. | Objectif | Attendu |
|---|---|---|
| S1 | Cadrage & Théorie | dépôt GitHub créé ; Docker installé ; liens vers les données / source choisie ; fiche de lecture théorique rendue ; schéma de base de données (quels modèles de `cours_derives` étendre) ; Gantt prévisionnel déposé |
| S2 | Prototype Python | formules écrites et expliquées ; algorithmes qui tournent sur un notebook |
| S3 | Extension Odoo | modèle Odoo étendu ; première capture d'écran des nouveaux champs calculés |
| S4 | Vues & IA (mi-parcours) | vues Odoo fonctionnelles ; modèle d'IA entraîné ; **rotation des rôles** ; Gantt mis à jour (prévu vs réalisé) |
| S5 | Intégration | le bouton Odoo déclenche l'IA ou le calcul complexe ; tests unitaires qui passent |
| S6 | Tests & Rédaction | module Odoo finalisé ; rapport final rédigé à 80 % ; Gantt inclus |
| S7 | Soutenance | rapport final (avec Gantt), code source zippé ; présentation orale de 15 minutes avec démonstration en direct |

- **Évaluation** : mini-comptes rendus 20 % ; code Python & maths 25 % ; intégration Odoo & IA 25 % ; rapport final 15 % ; soutenance 15 %.
- **Rôles (groupes de 4, semaines 1-4)** : Chef de projet / Finance (polycopié, rapport, cohérence financière, diapositives, Gantt) ; Quant / Data Python ; Développeur Odoo (extension de `cours_derives`, vues, boutons, PostgreSQL) ; Ingénieur IA / Testeur (modèle, pytest, intégration IA → Odoo). Rotation à la fin de la S4, visible sur le Gantt. Pour 5 : proposition du groupe dans `README.md` (qualité & intégration séparée de l'IA), à valider.
- **Discipline GitHub** : un dépôt par groupe créé en S1 ; au moins 1 commit par semaine et par étudiant ; message avec nom ou initiales, forme `[Prénom] verbe + objet` ; branches courtes ; pull requests relues par un autre membre. **Un nom jamais présent dans l'historique entraîne une note individuelle et non collective.**
- **Gantt** : prévisionnel déposé en S1, réalisé mis à jour à chaque séance ; le **Gantt réalisé est un livrable final obligatoire** dans le rapport ; la source éditable est aussi versionnée.
- **Structure du dépôt (annexe A)** : `README.md`, `docs/` (fiche de lecture, Gantt, schéma BDD, rapport), `notebooks/` (`01_donnees`, `02_modele_python`, `03_ia`), `src/` (`pricing.py`, `data.py`, `ml.py`), `tests/test_pricing.py`, `odoo_addons/cours_derives/`, `docker-compose.yml`, `requirements.txt`.

## 4. Ce que révèlent les supports de cours (TP 0)

Fournis par Wilfried, **hors dépôt** : `chap2.pdf` (cours), `TD2_Produits_derives_Enonces.pdf`, `TP_Chap2_Odoo.pdf`, `TP_Chap2_Python.pdf`, et un notebook de révision `Finance_Derives_Portefeuille_Odoo_cours_complet.ipynb` (cours, TD2 et TD3 résolus).

- **Le TP 0 est le TP Chap. 2 Odoo** : module `cours_derives` avec `cours.forward` (`name`, `S0`, `r`, `T`, `F0` calculé), `cours.option` (`name`, `option_type`, `S_T`, `K`, `premium`, `payoff`, `profit`) et `cours.portfolio` (deux actifs : `mu_A`, `sigma_A`, `mu_B`, `sigma_B`, `rho`, `w_A`, `w_B`, `exp_return`, `sigma_p`). Le cours (chap. 2 §2.8.2) nomme le champ `type` ; le TP `option_type`. La parité y est une méthode `put_par_parite(C, S0, K, r, T)`, pas un wizard.
- **Conséquence centrale** : `cours.option` n'a ni `spot`, ni `maturite`, ni `taux`, ni `volatilite`. `S_T` est le prix à l'échéance (pour le payoff), pas le spot d'aujourd'hui. Le code Odoo du guide suppose ces champs : **il faut les ajouter**. « Ajouter volatilité et prix si absents » sous-estime le travail.
- **Docker du TP** : `postgres:15` + `odoo:17.0`, port 8069, `./addons:/mnt/extra-addons`. Preuve d'installation attendue : capture de la page Applications avec le mode développeur. Si Odoo 18 : `<tree>` devient `<list>`.
- **Tests du TP** : `TransactionCase` Odoo (`@tagged("post_install", "-at_install")`), lancés par `docker compose run --rm web odoo -d mabase -u cours_derives --test-tags /cours_derives --stop-after-init`. Le guide demande en plus des tests **pytest** sur le code pur (`tests/test_pricing.py`).
- **Notebook de révision** : liste aussi `cours.markowitz`, `cours.capm`, `cours.volatility` (historique, EWMA), `cours.binomial` (TD3, champs `spot`, `strike`, `rate`, `volatility`, `maturity`). On ignore si ces modèles font partie du module réel du groupe : **demander `addons/cours_derives`**.
- **Valeurs de référence du cours** : forward `S0=80, r=4 %, T=0,5` ⇒ `F0=81,62` ; BS(100, 100, 5 %, 1 an, 20 %) ⇒ call 10,4506.
- Le chap. 2 §2.9 contient l'ancien cahier des charges du projet (forward + option, tableau de bord, IA scikit-learn de volatilité, rapport de 5 pages) et §2.8.3 annonce les thèmes d'IA : GARCH/LSTM, σ implicite par réseau, détection d'anomalies.

## 5. Décisions prises et points à trancher

| Sujet | Décision | Statut |
|---|---|---|
| Unités | `T` en années (jours calendaires / 365) ; `r` continu décimal ; `sigma` annualisée décimale ; theta par an (option `theta_per_day` : /365) ; vega pour 1,00 de σ (option `vega_per_pct` : /100) ; rho pour 1,00 de r | figé dans `CONVENTIONS.md` ; à communiquer aux G4, G5, G6, G7, G9 |
| Volatilité historique | `std(r_t, ddof=1) × √252` | figé |
| Loi normale | `scipy.special.ndtr` si SciPy présent, sinon `math.erf` (image Odoo sans SciPy) | figé, testé à 1e-15 |
| Cas `T = 0` ou `σ = 0` | prix = valeur intrinsèque actualisée au forward ; Grecques = limites déterministes (delta en escalier, gamma = vega = 0) ; **pas d'exception** | figé |
| Entrées invalides | `ValueError` (`S ≤ 0`, `K ≤ 0`, `T < 0`, `σ < 0`, `kind` inconnu) ; l'appelant Odoo doit les intercepter | figé |
| Nom des champs Odoo | celui du guide (`spot`, `strike`, `maturite`, `taux`, `volatilite`, `type`) pour l'instant | **à figer** après lecture du module réel et accord avec G4 et G7 |
| `strike` vs `K` | `strike` alias ou champ lié à `K` existant | **à trancher** |
| Vue graphique Delta(S) | modèle de points (One2many créé par le bouton) ou image matplotlib en base64 | **à trancher en S3** |
| IA dans Odoo | entraîner hors Odoo ; inférence seule (ONNX/onnxruntime via Dockerfile `FROM odoo:17`, ou petit service séparé) ; TensorFlow absent de l'image | **à trancher en S4** |
| Cible du LSTM | cible tournée vers l'avenir, sans chevauchement ; références persistance, EWMA λ = 0,94, GARCH(1,1) (`arch`) ; RMSE et QLIKE ; historique 10 ans | proposé, à valider avec le groupe |
| Lien IA ↔ pricing | agréger la prévision sur la maturité ; Odoo affiche « prix avec σ historique » et « prix avec σ prédite » côte à côte | proposé |
| Rôles à 5 | chef de projet ; quant / data ; dév. Odoo ; ingénieur IA ; qualité & intégration | proposé, à attribuer |

## 6. Arborescence du dépôt et rôle de chaque fichier

| Chemin | Contenu | État |
|---|---|---|
| `src/pricing.py` | `N`, `phi`, `bs_price`, `greeks`, `put_call_parity_gap` ; scalaires et tableaux NumPy | fait, testé |
| `src/data.py` | `load_prices_info` (yfinance puis CSV de repli, renvoie aussi la source `"yfinance"` ou `"csv"`), `load_prices` (même contrat qu'en S1), `simulate_gbm_prices` (graine 42), `log_returns`, `historical_volatility`, `rolling_realized_vol` | fait, testé hors réseau |
| `src/ml.py` | entraînement / inférence du LSTM | **absent** (S3-S4) |
| `tests/test_pricing.py` | 20 tests pytest | fait, verts |
| `tests/test_data.py` | 5 tests sans réseau (faux module yfinance) : source yfinance, repli CSV, erreur sans CSV, contrat de `load_prices`, rendements et volatilités | fait, verts |
| `pytest.ini` | `pythonpath = src` : les tests importent `from pricing import …` ; Odoo importe aussi `pricing` via `PYTHONPATH` | fait |
| `odoo_addons/cours_derives/` | README seulement | **à remplir** (S3) |
| `notebooks/` | vide (`.gitkeep`) | à faire (S2 : `01_donnees`, `02_modele_python` ; S3-S4 : `03_ia`) |
| `docs/fiche_lecture.pdf` | fiche de lecture Phase 0, 2 pages, 8 références | fait ; membres à compléter |
| `docs/gantt_previsionnel.png`, `docs/gantt_source.xlsx` | Gantt S1-S7, 21 tâches, 6 phases, jalons ; xlsx avec grille Prévu et grille Réalisé pilotées par des formules | fait |
| `docs/gantt_realise.png` | Gantt réalisé (**livrable final obligatoire**) | à produire en S4 puis S7 |
| `docs/schema_bdd.png` | extension de `cours.option` + `cours.vol.serie` + `cours.vol.prediction` | fait (version S1) |
| `docs/COMPRENDRE.md` | ce que l'équipe doit comprendre, valeurs de référence, 10 questions de soutenance | fait |
| `docs/MATIERE.md` | la matière dans son ensemble : dérivés, binomial, Black-Scholes, volatilité, portefeuille, CAPM, carte des 10 projets, Odoo, IA, formulaire, pièges ; parties « hors supports » signalées | fait |
| `docs/mini_cr_S1.md` | brouillon du mini-compte rendu S1 (cases à cocher) | fait ; à reporter dans le modèle du professeur |
| `docs/rapport/` | sources du rapport | vide |
| `tools/build_fiche.py`, `tools/build_gantt.py`, `tools/schema.dot` | régénèrent les documents de `docs/` | fait |
| `CONVENTIONS.md`, `README.md`, `requirements.txt`, `docker-compose.yml`, `.gitignore` | voir §5 | faits |

Régénérer les documents : `python3 tools/build_fiche.py`, `python3 tools/build_gantt.py`, `dot -Tpng -Gdpi=130 tools/schema.dot -o docs/schema_bdd.png` (polices DejaVu sous `/usr/share/fonts/truetype/dejavu/`, Graphviz installé).

## 7. Contrat de `src/pricing.py`

```python
bs_price(S, K, T, r, sigma, kind="call") -> float | ndarray
greeks(S, K, T, r, sigma, kind="call", theta_per_day=False, vega_per_pct=False)
    -> {"delta", "gamma", "vega", "theta", "rho"}
put_call_parity_gap(C, P, S, K, T, r)   # nul sans arbitrage
```

Valeurs de référence (S = K = 100, T = 1, r = 5 %, σ = 20 %) : call 10,4506 ; put 5,5735 ; call Delta 0,6368, Gamma 0,0188, Vega 37,524, Theta −6,414, Rho 53,2325 ; put Delta −0,3632, Theta −1,6579, Rho −41,8905 ; avec `theta_per_day` et `vega_per_pct` : theta call −0,01757, vega 0,37524. **Ne jamais changer la signature ni les unités par défaut sans prévenir les autres groupes.**

Tests : valeur connue ; identité avec le code du guide recopié (rel 1e-12) ; parité sur 243 combinaisons ; différences finies pour les cinq Grecques ; équation de Black-Scholes `Theta + ½σ²S²Γ + rSΔ − rV = 0` ; relations call/put ; limites ; cas dégénérés ; entrées invalides ; vectorisation ; unités ; `N` face à SciPy et à `math.erf` ; volatilité historique sur GBM simulé. `tests/test_data.py` : source yfinance, repli CSV, erreur sans CSV, contrat de `load_prices`, rendements et volatilités, sans réseau.

## 8. État d'avancement (10/11/2026, soir)

**Fait**
- [x] Dépôt local construit selon l'annexe A, 20 tests pytest verts (25 depuis S2-03), archive `projet-groupe1.zip` livrée à Wilfried.
- [x] Pricer Black-Scholes et Grecques (au-delà du guide : cas limites, validation, unités alternatives, repli sans SciPy).
- [x] Fiche de lecture, Gantt prévisionnel (png + xlsx), schéma de base de données, README, CONVENTIONS, docker-compose, brouillon du mini-compte rendu S1, `docs/COMPRENDRE.md`.
- [x] Syntaxe de `docker-compose.yml` validée (`docker compose config`).
- [x] Dépôt GitHub privé `wekt2k04/projet-groupe1-pricer-options-grecques` créé par Wilfried (S1-01), rattaché à Claude ; `.gitignore` laisse passer `data/*_fallback.csv`.
- [x] §9 réécrit en étapes atomiques (identifiant, responsable, commandes, preuve, repli).
- [x] `docs/MATIERE.md` : la matière dans son ensemble, tirée du chapitre 2, des TD 2 et 3, du TP Odoo et du notebook de révision.
- [x] S2-03 en avance : `load_prices_info` et `tests/test_data.py` ; 25 tests verts.

**Non vérifié (à ne pas affirmer comme acquis)**
- [ ] Démarrage réel d'Odoo avec ce `docker-compose.yml` ; import de `pricing` via `PYTHONPATH=/mnt/finance_src` dans le conteneur.
- [ ] `yfinance` (réseau Yahoo non joignable depuis l'environnement de Claude) ; `requirements.txt` complet (TensorFlow selon la version de Python).
- [ ] Le fichier xlsx dans Excel / LibreOffice (formules `IF/AND` relues, non recalculées).

**Pas encore fait**
- [ ] Réglages du dépôt `wekt2k04/projet-groupe1-pricer-options-grecques` (S1-02, S1-05) : inviter les 4 autres membres (Settings → Collaborators), ajouter les topics et, si l'offre GitHub le permet, protéger `main` (pull request + 1 approbation). Le premier commit est poussé (S1-03) ; clone de Claude : `/home/claude/projet-groupe1-pricer-options-grecques`.
- [ ] Notebooks, `src/ml.py`, module Odoo, vues, bouton, LSTM, rapport, Gantt réalisé.
- [ ] Noms et rôles des membres (README et Gantt).
- [ ] Mini-compte rendu au format du professeur.

## 9. Plan d'exécution — étapes atomiques

**Mode d'emploi.** Chaque étape a un identifiant, un responsable, des prérequis, les commandes ou fichiers exacts, une **Preuve** (ce qu'il faut montrer avant de cocher) et, quand c'est utile, un **Repli**. On ne coche une étape qu'avec sa preuve. Une étape aboutit à un commit au message `[Prénom] verbe + objet`. Rôles : **CP** chef de projet, **QD** quant / data, **DO** développeur Odoo, **IA** ingénieur IA, **QI** qualité et intégration (attribution à faire, §9.0). **Claude** exécute ce qui l'est dans son environnement ; ce qui exige l'ordinateur de Wilfried, un réseau libre, Docker ou la présence d'un membre est marqué **[Wilfried]** ou **[membre]**. Une étape de la semaine N+1 ne démarre qu'après la preuve de la semaine N, sauf mention de parallélisme (la préparation des données de l'IA démarre en S3).

### 9.0 Bloquants ouverts

| # | Bloquant | Détenu par | Ce qu'il permet | Repli en attendant |
|---|---|---|---|---|
| B1 | Identifiants GitHub des 4 autres membres, invitations envoyées | Wilfried | S1-02, toute contribution des autres | aucun : sans invitation, leurs commits n'existent pas, ce qui entraîne une note individuelle selon le guide ; relancer |
| B2 | Dossier `addons/cours_derives` du groupe (TP 0 réel) | Wilfried | S3 | reconstruire le minimum depuis §4 (champs `name`, `option_type`, `S_T`, `K`, `premium`, `payoff`, `profit`) et le signaler comme reconstruit |
| B3 | Modèle de mini-compte rendu du Drive | Wilfried | S1-10 | reporter `docs/mini_cr_S1.md` dans le modèle dès réception |
| B4 | Attribution des 5 rôles et ordre des présentateurs | le groupe, séance S1 | README, Gantt, S4 (rotation) | utiliser les rôles proposés ; Claude n'écrit aucun nom d'étudiant dans le dépôt |
| B5 | Date réelle de la séance S2 | professeur | Gantt | garder 18/11 comme indicatif |
| B6 | Identifiant GitHub du professeur | professeur | accès en lecture | demander en séance S1 |
| B7 | Machine avec Internet et Python pour produire les CSV de repli | [membre] | S2-02, S4-01 | simulation GBM étiquetée « simulée » dans chaque notebook |

### 9.1 S1 — avant la séance (nuit du 10/11 et matin du 11/11)

- [x] **S1-01 Dépôt créé** — Wilfried. Preuve : `https://github.com/wekt2k04/projet-groupe1-pricer-options-grecques`, privé, vide, rattaché à Claude (accès `push`).
- [ ] **S1-02 Inviter les 4 membres** — [Wilfried]. GitHub → Settings → Collaborators → Add people, accès *Write*. Preuve : 4 invitations « Pending » ou acceptées.
- [x] **S1-03 Premier push sur `main`** — fait par Claude le 10/11/2026 sur demande explicite de Wilfried (« Pousse »), voie B ; auteur et committer réécrits ensuite à sa demande en `Wilfried <190079580+wekt2k04@users.noreply.github.com>` (adresse anonyme GitHub liée à son profil), puis lignes d'attribution à Claude retirées à sa demande : il doit apparaître comme seul committer ; `CLAUDE.md` reste dans le dépôt, ce qui lui convient. Preuve : premier commit de `main` (`git log --reverse --oneline | head -1`). Procédure conservée pour mémoire : Le premier commit va **directement sur `main`** : un dépôt vide n'a pas de branche de base, donc pas de pull request possible, et GitHub ferait de la première branche poussée la branche par défaut. À partir du deuxième changement : branche + PR (§9.9 P2).
  Voie A, Wilfried sur un ordinateur :
  ```bash
  git config user.name && git config user.email      # l'e-mail doit être celui du compte GitHub
  unzip projet-groupe1.zip && cd projet-groupe1
  python -m venv .venv && source .venv/bin/activate  # Windows : .venv\Scripts\activate
  pip install numpy scipy pandas matplotlib pytest yfinance
  pytest                                             # attendu : 25 passed
  git init -b main && git add . && git status        # vérifier l'absence de .venv et de __pycache__
  git commit -m "[Wilfried] Ajout du squelette, du pricer Black-Scholes et des tests"
  git remote add origin https://github.com/wekt2k04/projet-groupe1-pricer-options-grecques.git
  git push -u origin main
  ```
  Voie B, Claude, depuis le clone vide :
  ```bash
  cd /home/claude/projet-groupe1-pricer-options-grecques && git fetch origin
  tar -C /home/claude/projet-groupe1 --exclude=.git --exclude=__pycache__ --exclude=.pytest_cache --exclude=.venv -cf - . | tar -xf -   # rsync absent de l'environnement
  python -m pytest -q                                # 25 passed, sinon arrêt
  git status --short                                 # relire : ni .venv, ni cache, ni .pyc
  git add -A
  git commit -m "[Wilfried] Ajout du squelette, du pricer Black-Scholes et des tests"   # identité et absence d'attribution : §11
  git push -u origin main
  ```
  Ne jamais utiliser l'e-mail personnel de Wilfried : l'identité à employer est son adresse anonyme GitHub (§11). Preuve : `git ls-remote origin` liste `refs/heads/main` ; la page GitHub affiche les dossiers `src`, `tests`, `docs`.
- [ ] **S1-04 Contrôle sur GitHub** — Claude ou membre. Le README s'affiche, `docs/COMPRENDRE.md` s'ouvre depuis le lien, les images `docs/*.png` s'affichent, aucun `.venv` ni `__pycache__`. Preuve : liste des anomalies, vide si tout va bien.
- [ ] **S1-05 Réglages du dépôt** — [Wilfried]. (a) Settings → Branches → règle sur `main` : exiger une pull request et 1 approbation ; si l'offre GitHub l'interdit pour un dépôt privé, écrire la règle d'équipe dans le README (déjà fait) et la respecter. (b) Topics : `black-scholes`, `options-pricing`, `greeks`, `odoo`, `python`, `lstm`, `volatility-forecasting`, `quantitative-finance`. (c) Ajouter le professeur en lecture dès B6. Faire (a) **après** S1-03.
- [ ] **S1-06 Odoo lancé et capture** — [membre] avec Docker. `docker compose up -d`, ouvrir `http://localhost:8069`, créer la base `mabase` (celle que suppose la commande de test du compose), activer le mode développeur (Réglages, bas de page, ou `?debug=1` dans l'URL), ouvrir **Applications**. Si le port 8069 est pris : `"8070:8069"` dans le compose. Preuve : capture `docs/captures/s1_odoo_applications.png` (créer le dossier). Ce que la capture prouve : Docker et Odoo démarrent, ce qui ferme la ligne « Non vérifié » du §8 pour le démarrage seulement, pas pour l'import de `pricing`.
- [ ] **S1-07 Un commit nominatif par membre** — chacun. Branche `<prenom>-role-s1`, modifier **sa propre ligne** du tableau « Équipe et rôles » du README, `git push`, ouvrir une PR vers `main`, relue par un autre membre. Preuve : PR fusionnée avec le prénom dans le message. Cette PR satisfait « 1 commit par semaine et par étudiant » pour la S1.
- [ ] **S1-08 Fiche de lecture** — CP. Relire `docs/fiche_lecture.pdf` ; ajouter les noms des membres dans `tools/build_fiche.py` (repérer l'emplacement : `grep -n -i membre tools/build_fiche.py`), puis `python3 tools/build_fiche.py`. Preuve : PDF régénéré, 2 pages, lien vers le fichier dans la PR.
- [ ] **S1-09 Gantt prévisionnel** — CP. Rien à régénérer sauf si les dates S2 changent (`DATES` dans `tools/build_gantt.py`, puis `python3 tools/build_gantt.py`). Preuve : `docs/gantt_previsionnel.png` et `docs/gantt_source.xlsx` présents dans `main`.
- [ ] **S1-10 Mini-compte rendu S1** — CP. Recopier `docs/mini_cr_S1.md` dans le modèle du professeur (B3) en ne cochant que ce qui a une preuve : S1-03 (dépôt), S1-06 (Docker), fiche (S1-08), schéma, Gantt (S1-09), pricer et 20 tests. Preuve : le document prêt avant la séance.

### 9.2 S1 — déroulé de la séance du 11/11 (10 minutes, un seul présentateur)

| Minute | Contenu | Support |
|---|---|---|
| 0 – 1 | Projet 1, rôle de socle pour les groupes 4, 5, 6, 7, 9 | `README.md` |
| 1 – 3 | Dépôt, discipline Git, équipe | page GitHub, historique des commits |
| 3 – 5 | Schéma de base de données et décision d'étendre `cours.option` avec de nouveaux champs | `docs/schema_bdd.png`, `docs/COMPRENDRE.md` §7 |
| 5 – 7 | Pricer en avance : `pytest` à 20 réussites, valeurs de référence (call 10,4506, Delta 0,6368) | terminal |
| 7 – 8 | Gantt prévisionnel, jalons S4 et S7 | `docs/gantt_previsionnel.png` |
| 8 – 10 | Questions au professeur et décisions à valider | liste ci-dessous |

Questions à poser, dans cet ordre : (1) alignement des noms de champs avec les groupes 4 et 7 (`spot`, `strike`, `maturite`, `taux`, `volatilite`) ; (2) date de la S2 (18/11 férié) ; (3) son identifiant GitHub ; (4) le module `cours_derives` de départ est-il celui du TP 0 tel quel ; (5) format attendu pour la rotation des présentateurs. **Ordre des présentateurs** : un membre différent par semaine, fixé en séance, à noter dans `docs/mini_cr_S2.md`. **S1-11 Après la séance** — Claude : reporter les réponses dans §5 et §9.0, cocher §8, ajouter une ligne au §12, régénérer le zip.

### 9.3 S2 — Prototype Python (critère du guide : formules écrites et expliquées, algorithmes qui tournent sur un notebook)

- [ ] **S2-01 Environnement de chaque membre** — [membre]. Python 3.10 à 3.12, `python -m venv .venv`, `pip install numpy scipy pandas matplotlib pytest yfinance jupyter nbconvert ipykernel nbformat`, puis `pytest`. Preuve : `25 passed` collé dans la PR du membre.
- [ ] **S2-02 CSV de repli AAPL 2 ans** — [membre] avec Internet. Le `.gitignore` exclut `data/*.csv` **sauf** `data/*_fallback.csv` (exception ajoutée) :
  ```python
  import sys; sys.path.insert(0, "src")
  from data import load_prices
  p = load_prices("AAPL", "2y"); p.rename("Close").to_csv("data/aapl_2y_fallback.csv", index_label="Date")
  ```
  Preuve : fichier de ~500 lignes, colonnes `Date,Close`, versionné. Repli : B7.
- [x] **S2-03 Source de données identifiable** — Claude (QD), faite le 10/11 en avance de phase. Ajouter à `src/data.py` `load_prices_info(ticker, period, csv_fallback) -> (prices, source)` avec `source` dans `{"yfinance", "csv"}` ; **ne pas modifier `load_prices`** (contrat §7). Tests dans `tests/test_data.py`, dont : repli CSV quand yfinance est indisponible (monkeypatch de `yfinance.download` pour lever une exception), et `RuntimeError` sans CSV. Preuve : `pytest` donne 25 passed (5 tests dans `tests/test_data.py`).
- [ ] **S2-04 `notebooks/01_donnees.ipynb`** — QD. Cellules, dans l'ordre : (1) markdown objectif ; (2) `sys.path.insert(0, "../src")` et imports ; (3) `prices, SOURCE = load_prices_info("AAPL", "2y", "../data/aapl_2y_fallback.csv")` puis `print("SOURCE =", SOURCE)` (si `csv` ou simulé, le dire en markdown) ; (4) nombre d'observations, première et dernière date, valeurs manquantes ; (5) `log_returns`, `historical_volatility` (formule rappelée en markdown : `std(r_t, ddof=1) × √252`) ; (6) deux graphiques enregistrés dans `docs/figures/` : `fig_01_prix.png`, `fig_02_vol_realisee_5j.png` ; (7) cellule finale qui affiche σ historique, réutilisée par `02`. Preuve : exécution de bout en bout sans erreur.
- [ ] **S2-05 `notebooks/02_modele_python.ipynb`** — QD. Cellules : (1) cas de référence `S=K=100, T=1, r=0.05, σ=0.20` avec `assert` sur les valeurs de §7 (tolérance 1e-3) ; (2) cas AAPL : `S0` = dernier cours, `K = round(S0)` (à la monnaie), `T = 30/365`, `σ` = valeur de `01`, `r` saisi à la main et annoté « hypothèse, à sourcer » (ne pas inventer un taux de marché) ; (3) Delta et Gamma en fonction de `S` de `0,5·K` à `1,5·K`, call et put, `fig_03_delta.png`, `fig_04_gamma.png` ; (4) les cinq Grecques par différences finies contre l'analytique, mêmes pas que `tests/test_pricing.py` (relire le fichier avant), tableau d'écarts relatifs ; (5) parité `C − P` contre `S − K·e^{−rT}` ; (6) prix en fonction de `σ` et de `T`, `fig_05_sensibilites.png` ; (7) tableau récapitulatif en markdown. Preuve : exécution sans erreur, `assert` passés.
- [ ] **S2-06 Exécution des notebooks** — Claude ou membre : `jupyter nbconvert --to notebook --execute --inplace notebooks/01_donnees.ipynb notebooks/02_modele_python.ipynb`. **Règle** : Claude exécute dans son bac à sable sans accès à Yahoo ; ses sorties reposent alors sur le CSV ou sur la simulation GBM et la cellule `SOURCE` le montre. Le notebook final destiné au rapport est ré-exécuté par un membre avec Internet. Preuve : `SOURCE = yfinance` dans la version du rapport.
- [ ] **S2-07 Gantt, colonnes réelles** — CP. Dans `docs/gantt_source.xlsx`, feuille `Gantt`, lignes 5 à 25 : colonnes F (début réel, numéro de semaine), G (fin réelle), H (statut : À faire, En cours, Terminé). Les grilles Prévu (J à P) et Réalisé (R à X) se calculent par formules ; ne pas les écraser. Preuve : fichier versionné ; S1 marquées « Terminé » avec les semaines réelles.
- [ ] **S2-08 Mini-compte rendu S2** — présentateur désigné en S1. Créer `docs/mini_cr_S2.md` sur le modèle de `docs/mini_cr_S1.md` (Réalisé, Décisions, Difficultés, Prévu). Preuve : fichier avant la séance.
- [ ] **S2-09 Commits nominatifs** — chaque membre, une PR dans la semaine (le contenu est libre mais réel : notebook, test, figure, relecture écrite d'une PR).

### 9.4 S3 — Extension Odoo (critère : modèle étendu, première capture des nouveaux champs calculés)

- [ ] **S3-01 Récupérer le module réel** — Claude réclame B2 ; copie dans `odoo_addons/cours_derives/` ; lire `__manifest__.py`, `models/`, `views/`, `security/`. Preuve : liste des champs réels de `cours.option` consignée en §4, nom exact du champ de type (`type` ou `option_type`).
- [ ] **S3-02 Base saine avant modification** — DO. `docker compose run --rm web odoo -d mabase -i cours_derives --stop-after-init`, puis les tests existants du module. Preuve : installation sans erreur, capture du modèle d'origine.
- [ ] **S3-03 Figer les noms de champs** — CP avec G4 et G7. Trancher `strike` (champ propre ou `related` de `K`) et le nom du type. Consigner dans §5 et `CONVENTIONS.md`, prévenir les groupes. Défaut si aucune réponse avant S3-05 : noms du guide (`spot`, `strike`, `maturite`, `taux`, `volatilite`), champ de type du module réel, `strike` en champ propre, et écrire « défaut appliqué » dans §5.
- [ ] **S3-04 Modèle étendu** — DO. Fichier `models/option_bs.py`, importé dans `models/__init__.py`. Squelette **indicatif, non exécuté**, à vérifier au lancement :
  ```python
  from odoo import api, fields, models
  from odoo.exceptions import ValidationError
  from pricing import bs_price, greeks            # PYTHONPATH=/mnt/finance_src (docker-compose.yml)

  class CoursOptionBS(models.Model):
      _inherit = "cours.option"
      ticker = fields.Char()
      spot = fields.Float(digits=(16, 4)); strike = fields.Float(digits=(16, 4))
      maturite = fields.Float(digits=(16, 6), help="années")
      taux = fields.Float(digits=(16, 6), default=0.05); volatilite = fields.Float(digits=(16, 6), default=0.20)
      prix_bs = fields.Float(compute="_compute_bs", store=True, digits=(16, 4))
      greeks_delta = fields.Float(compute="_compute_bs", store=True, digits=(16, 6))   # idem gamma, vega, theta, rho

      @api.depends("spot", "strike", "maturite", "taux", "volatilite", "<champ_type>")
      def _compute_bs(self):
          for rec in self:
              try:
                  rec.prix_bs = bs_price(rec.spot, rec.strike, rec.maturite, rec.taux, rec.volatilite, rec["<champ_type>"])
                  g = greeks(rec.spot, rec.strike, rec.maturite, rec.taux, rec.volatilite, rec["<champ_type>"])
                  rec.greeks_delta = g["delta"]    # et gamma, vega, theta, rho
              except ValueError:                   # entrée invalide : ne jamais faire planter le formulaire
                  rec.prix_bs = rec.greeks_delta = 0.0

      def action_calculer(self):
          for rec in self:
              rec._compute_bs()
          return True
  ```
  Si `import pricing` échoue dans le conteneur : vérifier `docker compose exec web python3 -c "import pricing"` et la variable `PYTHONPATH` ; **repli** : copier `src/pricing.py` dans le module et le dire dans le rapport. Contraintes `@api.constrains` : `spot > 0`, `strike > 0`, `maturite >= 0`, `volatilite >= 0`, message en français. Preuve : mise à jour du module sans erreur (`-u cours_derives`).
- [ ] **S3-05 Vue minimale** — DO. Vue formulaire héritée (`inherit_id` + `xpath`) qui ajoute les champs d'entrée et les Grecques, plus le bouton `<button name="action_calculer" type="object" string="Calculer"/>`. Version Odoo 17 : `<tree>`. Preuve : **capture d'écran S3** d'un enregistrement avec S = K = 100, T = 1, r = 0,05, σ = 0,20 montrant prix 10,4506 et Delta 0,6368.
- [ ] **S3-06 Tests Odoo** — QI. `tests/test_option_bs.py` du module, `TransactionCase`, `@tagged("post_install", "-at_install")`. Cas : valeurs de référence du call et du put (§7, `places=3` pour les prix, Delta, Rho ; `places=2` pour Vega et Theta), recalcul quand `spot` change, `maturite = 0` sans exception, `spot <= 0` lève `ValidationError`. Commande : `docker compose run --rm web odoo -d mabase -u cours_derives --test-tags /cours_derives --stop-after-init`. Preuve : sortie sans échec.
- [ ] **S3-07 Parallèle IA : données et références** — IA. `notebooks/03_ia.ipynb`, cellules 1 à 4 seulement : données AAPL 10 ans (`period="10y"`, CSV de repli `data/aapl_10y_fallback.csv`), construction des cibles (§9.5 S4-03), références persistance et EWMA(0,94), pas de TensorFlow encore. Python 3.10 à 3.12 requis pour la suite.
- [ ] **S3-08 Mini-compte rendu S3 et commits nominatifs.**

### 9.5 S4 — Vues, IA, mi-parcours (critère : vues fonctionnelles, modèle entraîné, rotation des rôles, Gantt mis à jour)

- [ ] **S4-01 Vues complètes** — DO. Formulaire avec groupes « Paramètres » et « Résultats / Grecques », liste, bouton « Calculer ». Preuve : captures des trois vues.
- [ ] **S4-02 Graphique Delta(S)** — DO. Le graphique Odoo agrège des enregistrements. **Défaut** : modèle `cours.option.point` (`option_id` Many2one, `moneyness_pct` entier de 50 à 150, `delta`, `gamma`) rempli par `action_calculer` ; vue `<graph type="line">` avec `moneyness_pct` en ligne et `delta` en mesure. Le regroupement sur un entier est à vérifier à l'exécution (le regroupement sur un flottant est peu fiable). **Repli** : image matplotlib en base64 dans un champ `Binary`. Un nouveau modèle exige `security/ir.model.access.csv`. Preuve : capture du graphique.
- [ ] **S4-03 LSTM** — IA. Spécification imposée par les pièges de §10 :
  1. **Variante conforme au guide (V0)** : entrée = 30 dernières volatilités réalisées sur 5 jours, cible = valeur du lendemain.
  2. **Variante rigoureuse (V1)** : entrée = 30 derniers rendements journaliers, cible = volatilité réalisée annualisée sur les 5 jours **suivants** (sans chevauchement avec l'entrée).
  3. Découpage chronologique 70 / 15 / 15 ; `MinMaxScaler` appris sur le train seul ; `tf.keras.utils.set_random_seed(42)` ; `LSTM(32)` puis `Dense(1)`, Adam, `EarlyStopping` sur la validation.
  4. Références sur le même jeu de test : persistance, EWMA λ = 0,94, GARCH(1,1) via `arch`.
  5. Métriques : RMSE et QLIKE (définition écrite dans le notebook). Tableau final V0 et V1 contre les trois références. **Si le LSTM perd, le dire** ; ne pas ajuster jusqu'à gagner.
  Preuve : notebook exécuté, tableau de résultats, courbe d'apprentissage.
- [ ] **S4-04 Export du modèle** — IA. **Défaut** : ONNX (`tf2onnx`) dans `models/lstm_vol.onnx`, inférence par `onnxruntime` dans une image Odoo dérivée (`Dockerfile` : `FROM odoo:17.0`, `USER root`, installation pip d'`onnxruntime`, `USER odoo` ; ajouter `--break-system-packages` si pip le refuse). **Repli** : le notebook écrit la dernière prévision dans `cours.vol.prediction` (import CSV) et le bouton Odoo lit cet enregistrement. Décision à consigner en §5.
- [ ] **S4-05 Rotation des rôles** — CP. Chaque membre prend un rôle qu'il n'a pas tenu en S1-S4 ; mettre à jour le tableau du README, le jalon « Rotation » du Gantt (déjà en S4) et la colonne Rôle du xlsx. Preuve : PR fusionnée.
- [ ] **S4-06 Gantt réalisé** — CP. Créer `tools/build_gantt_realise.py` : lit `docs/gantt_source.xlsx` (feuille `Gantt`, lignes 5 à 25, colonnes D à H, **sans** `data_only`), dessine barres prévues et réelles sur la même grille, écrit `docs/gantt_realise.png`. Preuve : image dans `main`, rappelée en séance.
- [ ] **S4-07 Mini-compte rendu S4 et commits nominatifs.**

### 9.6 S5 — Intégration (critère : le bouton Odoo déclenche l'IA ou le calcul complexe ; tests unitaires qui passent)

- [ ] **S5-01 Bouton complet** — DO + IA. `action_calculer` calcule le prix et les Grecques avec la volatilité saisie, puis `action_predire_vol` appelle l'inférence et remplit `prediction_id` (Many2one vers `cours.vol.prediction`).
- [ ] **S5-02 Prix côte à côte** — DO. `prix_bs_hist` (σ historique) et `prix_bs_lstm` (σ prédite) affichés ensemble, avec une note visible sur l'écart d'horizon (prévision à 5 jours, option de maturité `T`). Pas de conclusion sur une amélioration du prix.
- [ ] **S5-03 Tests** — QI. (a) purs : `pytest` ; (b) Odoo `TransactionCase` : calcul, bouton, contraintes, cas dégénérés ; (c) intégration : bouton → prédiction → `prix_bs_lstm` renseigné ; (d) échec contrôlé : modèle absent ou entrée invalide donne un message, pas une trace. Preuve : sorties des deux commandes de test.
- [ ] **S5-04 Mini-compte rendu S5 et commits nominatifs.**

### 9.7 S6 — Tests et rédaction (critère : module finalisé, rapport à 80 %, Gantt inclus)

- [ ] **S6-01 Gel fonctionnel** — plus de nouvelle fonctionnalité ; corrections seulement.
- [ ] **S6-02 Rapport** dans `docs/rapport/`, plan proposé : 1 contexte et objectifs ; 2 théorie (Black-Scholes, Grecques, parité) ; 3 données et volatilité ; 4 implémentation Python et validation ; 5 extension Odoo ; 6 IA, résultats et limites ; 7 Gantt prévu contre réalisé ; 8 contribution de chaque membre (`git shortlog -sn`) ; annexes. Toute figure provient d'un notebook ré-exécuté ; tout chiffre est recopié depuis la sortie, jamais de mémoire. Preuve : 80 % rédigé, Gantt réalisé inclus.
- [ ] **S6-03 Relecture croisée des chiffres** — QI : chaque nombre du rapport retrouvé dans une sortie exécutée.
- [ ] **S6-04 Mini-compte rendu S6 et commits nominatifs.**

### 9.8 S7 — Soutenance (15 minutes, démonstration en direct)

- [ ] **S7-01 Livrables** : rapport final avec Gantt réalisé ; code zippé par `git archive --format=zip -o projet-groupe1-final.zip HEAD` après fusion de toutes les PR ; vérifier que `pytest` passe dans une copie propre du zip.
- [ ] **S7-02 Déroulé proposé** : 0–1 contexte et équipe ; 1–4 théorie et conventions ; 4–7 démonstration Python ; 7–11 démonstration Odoo en direct ; 11–13 IA, résultats honnêtes ; 13–14 Gantt prévu contre réalisé, rotation ; 14–15 limites et conclusion. Chaque membre présente une partie.
- [ ] **S7-03 Répétition complète chronométrée**, deux fois, la dernière sur l'ordinateur de la soutenance.
- [ ] **S7-04 Plan B de démonstration** : base Odoo préparée avec un enregistrement par cas (call, put, `T = 0`), vidéo d'écran du parcours complet, captures dans les diapositives.
- [ ] **S7-05 Questions** : chacun répond aux 10 questions de `docs/COMPRENDRE.md` §9 sans notes.

### 9.9 Procédures transverses

**P1 — Reprise d'une session.** §0 ; puis `git -C <clone> fetch origin && git log --oneline -10 origin/main` pour voir ce que les autres ont changé ; puis la première étape non cochée ci-dessus.

**P2 — Contribuer après le premier commit** (toute session, tout membre : branche + PR, jamais de push direct sur `main`). La boucle humaine est détaillée en §14.5. Dans une session Claude :
```bash
cd <dossier du dépôt cloné>                         # session distante : /home/claude/projet-groupe1-pricer-options-grecques
git fetch origin main && git checkout main && git pull --ff-only origin main   # un clone superficiel en retard fait refuser le push (HTTP 413)
git checkout -b <prenom>-<id-etape>
python -m pytest -q                                 # avant tout commit de code
git add <fichiers précis>                           # relire git status ; pas de git add -A à l'aveugle
git commit -m "[Prénom] <verbe + objet> (<id étape>)"   # identité et attribution : §11, selon l'utilisateur
git push -u origin <prenom>-<id-etape>
gh pr create --base main --head <prenom>-<id-etape> --title "[Prénom] <verbe + objet>" --body "<étape, ce qui est fait, preuve>"
```
Si `gh pr create` est bloqué : `gh api repos/wekt2k04/projet-groupe1-pricer-options-grecques/pulls -f title=… -f head=… -f base=main -f body=…`, sinon ouvrir la PR sur github.com. **Claude ne fusionne jamais une PR** : la relecture par un autre membre est une exigence du guide.

**P3 — Mettre à jour le Gantt réalisé** : S2-07 chaque semaine (xlsx), S4-06 puis S7 pour l'image.

**P4 — Mini-compte rendu hebdomadaire** : créer `docs/mini_cr_S<n>.md` en début de semaine ; sections Réalisé (avec preuve), Décisions, Difficultés, Prévu ; ne cocher que le prouvé ; reporter dans le modèle du professeur ; le présentateur change chaque semaine.

**P5 — Régénérer les documents** : voir §6, dernière ligne.

**P6 — Terminer proprement une session Claude** : mettre à jour §8 et les cases de §9, ajouter une ligne au §12, relancer `pytest`, livrer le tout par une PR (P2).

## 10. Pièges connus

- **Cible du LSTM** : la volatilité glissante sur 5 jours au jour t+1 partage 4 rendements sur 5 avec celle du jour t ; la persistance bat ou égale un LSTM par construction. Avec 2 ans de cotations (~500 points, ~330 séquences d'entraînement à 70 %), l'échantillon est trop petit. Si le LSTM perd, le dire.
- **Variante « volatilité implicite future »** : irréalisable avec yfinance (photographie de la chaîne d'options du jour, pas d'historique).
- **Horizon** : une prévision à 1 jour ne se met pas dans le prix d'une option à 1 an.
- **Vue graphique Odoo** : agrège des enregistrements, ne trace pas une fonction.
- **Conteneur Odoo** : ni SciPy ni TensorFlow vraisemblablement ; `math.erf` pour la loi normale.
- **Champ calculé qui lève une exception** : fait planter le formulaire ; intercepter `ValueError` côté Odoo.
- **`T` en 365 jours, σ annualisée en 252** : décalage assumé, à expliquer à l'oral.
- **Noms divergents** : `type` / `option_type` / `strike` / `K` ; `S_T` n'est pas le spot.
- **`type` masque la fonction intégrée `type` de Python** (critiqué dans la correction du TD3) : préférer `option_type` si le module réel le permet.
- **Environnement de Claude** : réseau limité (PyPI et GitHub, pas Yahoo) ; Docker présent mais Odoo non testé ; NumPy 2, SciPy, pandas, scikit-learn, pytest, reportlab, openpyxl, matplotlib installés ; TensorFlow, PyTorch, `arch`, `yfinance` absents.

## 11. Règles de travail pour Claude (toutes sessions)

- **Langue et style** : français par défaut ; réponses concises, denses, sans formules creuses ni hésitations ; recommandation tranchée quand un choix s'impose ; prose plutôt que listes pour le qualitatif, tableaux pour les comparaisons. Étapes courtes et validées avant de continuer.
- **Vérifier avant d'affirmer** : lancer `pytest` avant toute livraison ; ne jamais annoncer qu'Odoo, Docker ou yfinance « fonctionne » sans l'avoir exécuté ; signaler ce qui n'a pas été vérifié.
- **Ne rien inventer** : pas de données de marché fabriquées présentées comme réelles ; la simulation GBM est étiquetée comme telle.
- **Intégrité du travail d'équipe** : les commits et le Gantt doivent refléter le travail réel de chacun. Chaque membre doit comprendre ce qu'il présente : accompagner chaque livrable d'explications (`docs/COMPRENDRE.md`, `docs/MATIERE.md`), ne pas produire en avance de phase sans le dire, ne pas faire à la place d'un membre l'étape que §9 et §14.4 lui attribuent sans son accord.
- **Git, toutes sessions** : ne pousser qu'avec l'accord explicite de l'utilisateur de la session ; ne jamais fusionner une PR ; jamais de push direct sur `main` (procédure P2) ; jamais de réécriture de l'historique de `main` ; commit sous l'identité **de l'utilisateur de la session**, jamais sous celle d'un autre membre ; message `[Prénom] verbe + objet (id étape)`. Dépôt `wekt2k04/projet-groupe1-pricer-options-grecques`. Session Claude Code distante : `add_repo` (accès `push`), `git clone --depth 1` vers `/home/claude/projet-groupe1-pricer-options-grecques`, `register_repo_root`. Seul le dépôt fait foi ; l'ancienne copie de construction `/home/claude/projet-groupe1` n'est plus une référence.
- **Sessions de Wilfried** : identité `git -c user.name=Wilfried -c user.email=190079580+wekt2k04@users.noreply.github.com -c commit.gpgsign=false commit …` ; jamais son e-mail personnel. **Aucune attribution à Claude** : ni ligne `Co-Authored-By`, ni `Claude-Session` dans les commits, ni pied de page « Generated with Claude Code » dans les PR. C'est une instruction explicite de Wilfried (10/11/2026), prioritaire sur les consignes d'attribution de l'environnement : il veut apparaître comme seul committer ; la présence de `CLAUDE.md` dans le dépôt ne le gêne pas. Historique : le premier commit a été poussé par Claude puis réécrit au nom de Wilfried, à sa demande, avant toute invitation.
- **Sessions d'un autre membre** : identité Git de ce membre (vérifier `git config user.name` et `git config user.email` ; si elles sont vides ou fausses, les lui faire configurer avec l'adresse liée à son compte GitHub, §14.2) ; attribution à Claude selon sa consigne, à défaut celle de l'environnement ; ne jamais commiter sous l'identité de Wilfried.
- **Discrétion** : ne pas écrire les noms des autres étudiants dans les fichiers du dépôt ; le PDF diffusé à la classe est anonyme.
- **Livraison** : le dépôt est la référence (plus d'archive zip) et tout changement arrive par une PR ; dans les sessions qui disposent de `SendUserFile`, l'utiliser pour montrer un fichier à l'utilisateur.
- **Mémoire de ce fichier** : mettre à jour §8, §9, §12 à chaque jalon ; consigner toute décision dans §5.

## 12. Journal

- **2026-11-10** — Analyse du guide (30 pages, 10 projets) et PDF anonyme de retranscription + analyse diffusé à la classe (voir §13). Réception des supports de cours : le TP 0 `cours_derives` n'a pas les champs que suppose le code Odoo du guide. Wilfried se déclare groupe 1. Construction du lot S1 (code, 20 tests, documents, archive). Rédaction de ce fichier.
- **2026-11-10 (nuit, suite)** — Ajout du §14 « Guide du membre » ; règles de §11 scindées selon l'utilisateur de la session (Wilfried ou autre membre) ; P2 et P6 rendus valables pour tous ; fin de l'archive zip, le dépôt fait foi.
- **2026-11-10 (nuit)** — §9 réécrit en étapes atomiques ; correction : le premier commit va sur `main` (dépôt vide, pas de PR possible) ; `.gitignore` corrigé pour versionner `data/*_fallback.csv` ; `docs/MATIERE.md` rédigé ; S2-03 faite (25 tests). Premier commit poussé sur `main` par Claude à la demande de Wilfried (S1-03), puis auteur réécrit en Wilfried (adresse anonyme GitHub), lignes d'attribution à Claude retirées à sa demande, repoussé avec `--force-with-lease`, avant toute invitation.
- **2026-11-10 (soir)** — Wilfried crée le dépôt GitHub privé `wekt2k04/projet-groupe1-pricer-options-grecques` (vide, sans README ni licence) ; rattaché à la session de Claude avec accès `push`. Aucun commit poussé.

## 13. Livrables annexes hors dépôt

- **PDF de classe** : `Guide_Projets_Integrateurs_Retranscription_Analyse.pdf` (31 pages), retranscription complète et anonyme du guide plus une analyse critique, accompagné d'un message d'avertissement pour le groupe de la classe. Projets 1 à 10, annexe A et la majeure partie du glossaire recoupés avec des captures nettes ; restent non recoupés : les trois dernières lignes du glossaire et l'annexe C (effectifs : G1 5, G2 4, G3 5, G4 4, G5 4, G6 4, G7 5, G8 4, G9 5, G10 4 ; corps du guide : 4, 4, 4, 4, 3, 4, 4, 4, 4, 3). Le script générateur vit dans le répertoire temporaire d'une session précédente et peut avoir disparu.
- **Analyse du guide, points saillants** : le Projet 1 est le plus exposé du module ; six groupes ont un membre de plus en annexe C que dans le corps (quatre à 5 membres : G1, G3, G7, G9) ; le guide ne définit pas les conventions communes ni le contenu du TP 0.

## 14. Guide du membre (lecteur humain)

Cette section s'adresse à chaque membre du groupe qui ouvre le dépôt. Elle suffit pour s'installer, comprendre, trouver sa tâche et contribuer sans demander à personne. Le détail de chaque tâche est en §9.

### 14.1 Les règles qui comptent pour la note

| Règle | Source | Conséquence |
|---|---|---|
| Au moins **un commit par semaine et par membre**, prénom dans le message : `[Prénom] verbe + objet` | guide | un nom jamais présent dans l'historique entraîne une **note individuelle** et non collective |
| Toute modification passe par une **branche** et une **pull request relue par un autre membre** | guide | aucun push direct sur `main` |
| Un **mini-compte rendu** au début de chaque séance, à partir du 11/11/2026, présenté par un membre différent chaque semaine | message du professeur, guide | 20 % de la note ; présence obligatoire de tous |
| Le **Gantt réalisé** est mis à jour chaque semaine | guide | livrable final obligatoire |
| Chacun sait expliquer ce qu'il a commité | soutenance, mini-comptes rendus | questions individuelles possibles |

Barème : mini-comptes rendus 20 %, code Python et maths 25 %, intégration Odoo et IA 25 %, rapport 15 %, soutenance 15 %.

### 14.2 Installer une fois

Prérequis : un compte GitHub ; l'invitation au dépôt acceptée (lien reçu par e-mail ou `https://github.com/wekt2k04/projet-groupe1-pricer-options-grecques/invitations`) ; Git ; Python **3.10 à 3.12** (TensorFlow ne suit pas toujours la dernière version de Python) ; Docker Desktop pour Odoo.

```bash
git clone https://github.com/wekt2k04/projet-groupe1-pricer-options-grecques.git
cd projet-groupe1-pricer-options-grecques
git config user.name "<Prénom>"
git config user.email "<adresse liée à ton compte GitHub>"   # GitHub → Settings → Emails ; l'adresse « noreply » convient
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell : .venv\Scripts\Activate.ps1 ; cmd : .venv\Scripts\activate
pip install numpy scipy pandas matplotlib pytest yfinance jupyter nbconvert ipykernel nbformat
pytest                           # attendu : 25 passed
```

L'adresse de `user.email` doit être reliée à **ton** compte GitHub, sinon tes commits ne te sont pas attribués. Si PowerShell refuse d'activer l'environnement : `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. Garde la sortie `25 passed` : c'est la preuve de l'étape S2-01.

### 14.3 Lire pour comprendre, dans cet ordre

1. [`docs/MATIERE.md`](docs/MATIERE.md) : la matière (dérivés, binomial, Black-Scholes, volatilité, portefeuille, CAPM, Odoo, IA, carte des 10 projets).
2. [`docs/COMPRENDRE.md`](docs/COMPRENDRE.md) : notre projet, les valeurs de référence, les 10 questions probables de soutenance (§9).
3. [`CONVENTIONS.md`](CONVENTIONS.md) : les unités que les groupes 4, 5, 6, 7 et 9 reprennent de nous.
4. §2 et §3 de ce fichier : ce que le guide exige, semaine par semaine.

### 14.4 Trouver ta tâche

Ton rôle figure dans le tableau « Équipe et rôles » du README ; tu remplis toi-même ta ligne (étape S1-07). Les rôles tournent à la S4 (S4-05).

| Rôle | Étapes de §9 qui lui reviennent |
|---|---|
| CP — chef de projet | S1-05 (avec Wilfried), S1-08, S1-09, S1-10, S2-07, S3-03, S4-05, S4-06, S6-02, coordination du rapport |
| QD — quant / data | S2-02, S2-04, S2-05, S2-06 |
| DO — développeur Odoo | S1-06, S3-01, S3-02, S3-04, S3-05, S4-01, S4-02, S5-01, S5-02 |
| IA — ingénieur IA | S3-07, S4-03, S4-04, S5-01 (avec DO) |
| QI — qualité et intégration | S2-01 (vérifier chaque membre), S3-06, S5-03, S6-03, S7-01, relectures de PR |
| Tous | S1-07, S2-09 et l'équivalent chaque semaine, présentation tournante du mini-compte rendu, S7-02 à S7-05 |

**Règle de choix** : prendre, dans son rôle, la première étape non cochée dont les prérequis sont faits. **Pour la réserver**, ouvrir tout de suite une pull request en brouillon (*draft*) dont le titre commence par l'identifiant, par exemple `[Amine] S2-04 notebook des données`. Une étape déjà réservée par une PR ouverte n'est pas prise par quelqu'un d'autre.

### 14.5 Contribuer : la boucle complète

```bash
git checkout main && git pull                       # partir de la dernière version
git checkout -b <prenom>-<id-etape>                 # ex. amine-s2-04 : minuscules, sans accent
# … travailler ; pytest doit rester vert …
git add <fichiers précis>                           # relire git status avant
git commit -m "[Prénom] <verbe + objet> (<id étape>)"
git push -u origin <prenom>-<id-etape>
```

Sur GitHub : **Compare & pull request**, base `main`. Titre = message du commit. Description : l'étape, ce qui est fait, la **preuve** exigée par §9 (sortie de `pytest`, capture, chemin du fichier). Dans la même PR, **cocher l'étape dans §9 de ce fichier** et écrire sa preuve. Demander la relecture à un autre membre. Le relecteur lit, relance `pytest` si du code a changé, puis approuve ou commente. Après approbation, l'auteur fusionne (**Create a merge commit**, qui garde chaque commit nominatif) et supprime sa branche.

Si `git push` est refusé parce que `main` a avancé : `git fetch origin && git rebase origin/main`, relancer `pytest`, puis `git push --force-with-lease` **sur ta branche seulement**, jamais sur `main`.

### 14.6 La semaine type

Avant la séance, le présentateur de la semaine prépare `docs/mini_cr_S<n>.md` (procédure P4) ; le CP met à jour les colonnes réelles du Gantt (S2-07) ; chaque membre a au moins une PR ouverte ou fusionnée dans la semaine. Pendant la séance, 10 minutes de mini-compte rendu, tous présents. Après la séance, le CP reporte les décisions du professeur en §5 et une ligne dans §12.

### 14.7 Travailler avec Claude ou une autre IA

Claude Code lit ce fichier automatiquement à l'ouverture du dépôt. Commence la session en donnant ton prénom : les règles de §11 (identité Git, accord avant de pousser) en dépendent, et ta session commite sous **ton** identité, jamais sous celle d'un autre membre. Tu restes responsable de ce que tu commites : avant de fusionner, vérifie que tu sais l'expliquer, car les mini-comptes rendus et la soutenance comportent des questions individuelles.

### 14.8 Problèmes fréquents

| Symptôme | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'pricing'` | lancer `pytest` depuis la racine du dépôt (`pytest.ini` ajoute `src/` au chemin) ; dans un notebook : `sys.path.insert(0, "../src")` |
| yfinance renvoie une erreur ou une série vide | utiliser le CSV de repli `data/aapl_2y_fallback.csv` (S2-02) ; `load_prices_info` indique la source utilisée |
| `git push` vers `main` refusé | normal : passer par une branche et une PR (§14.5) |
| Port 8069 déjà pris | remplacer `"8069:8069"` par `"8070:8069"` dans `docker-compose.yml` |
| Odoo ne voit pas le module | `docker compose restart web`, puis mise à jour du module avec `-u cours_derives` |
| TensorFlow refuse de s'installer | vérifier `python --version` : utiliser 3.10 à 3.12 |
| Conflit dans `CLAUDE.md` | garder les deux modifications : chaque ligne de §9 est indépendante |

### 14.9 Ce qu'on ne fait jamais

Pousser directement sur `main` ; fusionner sa propre PR sans approbation ; réécrire l'historique de `main` (`--force`) ; versionner `.venv/`, des modèles `.keras` ou `.h5`, ou des CSV autres que `data/*_fallback.csv` ; changer la signature ou les unités de `bs_price` et `greeks` sans accord des groupes 4, 5, 6, 7, 9 (`CONVENTIONS.md`) ; écrire dans le dépôt des informations personnelles sur un camarade ; présenter des données simulées comme réelles.
