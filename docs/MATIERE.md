# La matière : Finance des Marchés et ERP, de la formule au module Odoo

Ce fichier explique **le module dans son ensemble** : les notions financières, la manière dont elles deviennent du code Python puis un module Odoo, et le rôle de l'IA. [`COMPRENDRE.md`](COMPRENDRE.md) se limite à **notre projet** (pricer et Grecques). On lit ce fichier-ci d'abord, puis `COMPRENDRE.md`.

Sources : chapitre 2 du cours (`chap2.pdf`), TD 2, TD 3 résolu dans le notebook de révision, TP Chap. 2 Odoo et Python, guide des projets intégrateurs 2026-2027. Ce qui ne vient pas de ces supports est signalé « *hors supports* » : formules standard de la littérature (Hull ; Bossu et Henrotte), utiles pour les projets mais à vérifier dans le cours quand il arrivera. Les chiffres des exemples sont ceux des supports ; ceux que ce fichier ajoute ont été recalculés avec `src/pricing.py`.

---

## 1. La logique du module : trois couches et une question

Le module enchaîne trois couches. La **finance** donne un prix ou un risque par une formule tirée du non-arbitrage ou de l'optimisation. **Python** calcule cette formule, la vérifie par des tests et la confronte aux données. **Odoo** rend le calcul utilisable dans une entreprise : des enregistrements en base PostgreSQL, des champs calculés, des vues, des boutons, des droits d'accès. L'**IA** se greffe là où une formule fermée ne suffit pas : prévoir une volatilité, calibrer un modèle, détecter une anomalie, couvrir avec des frictions.

Une seule question traverse le module : **quel est le prix juste d'un flux futur incertain, et comment l'entreprise le gère-t-elle au quotidien ?** Le chapitre 1, non fourni ici, traite les flux certains (obligations, actualisation, courbe des taux). Le chapitre 2 traite les flux incertains : dérivés, puis combinaison d'actifs risqués. Les dix projets intégrateurs prolongent chacun un morceau de cette chaîne (section 9).

## 2. Les trois idées qui expliquent presque tout

### 2.1 Le taux continu : pourquoi on écrit e^(rT) et non 1 + rT

Avec un taux continu `r`, 1 € placé pendant `T` années devient `e^(rT)` ; 1 € reçu dans `T` années vaut `e^(−rT)` aujourd'hui. Tout le chapitre 2 et le TD 2 utilisent cette convention (« taux continus » est écrit en tête du TD). Le premier piège d'examen du notebook de révision est d'écrire `S0(1 + rT)` au lieu de `S0·e^(rT)`.

### 2.2 Le non-arbitrage : le principe qui fixe les prix

Un arbitrage est une stratégie sans mise nette et sans risque qui rapporte à coup sûr. Un marché où il en existe ne reste pas à l'équilibre : les arbitragistes achètent le moins cher, vendent le plus cher, et les prix se rejoignent. Toute la théorie des dérivés du cours en découle. Le prix forward, la parité call-put et le prix binomial sont trois applications du même raisonnement : **deux portefeuilles qui paient la même chose à l'échéance doivent coûter la même chose aujourd'hui**.

### 2.3 La probabilité risque-neutre : un outil de calcul, pas une prévision

Le modèle binomial (TD 3) montre qu'on peut **répliquer** une option avec de l'action et un prêt ou emprunt. Le prix de l'option est le coût de cette réplication et ne dépend pas de la probabilité réelle de hausse. Le calcul revient à prendre l'espérance du payoff sous une probabilité fictive `q` (risque-neutre), puis à l'actualiser au taux sans risque. Sous `q`, l'action rapporte en moyenne le taux sans risque : `E_q[S_T] = S0·e^(rT)` (exercice 1 du TD 3). `q` n'est **pas** la probabilité réelle de hausse ; c'est le piège central du TD 3.

## 3. Les produits dérivés : vocabulaire, forward, futures

### 3.1 Le vocabulaire qu'il faut manier sans hésiter

| Terme | Définition opérationnelle |
|---|---|
| Produit dérivé | contrat dont la valeur dépend d'un actif **sous-jacent** (action, obligation, matière première, devise, indice, taux) |
| Forward | engagement ferme, **de gré à gré** (OTC), sur mesure, d'échanger l'actif en `T` au prix `F0` fixé aujourd'hui |
| Futures | forward **standardisé**, négocié en bourse, chambre de compensation, **appels de marge quotidiens** |
| Option | **droit** sans obligation d'acheter (**call**) ou de vendre (**put**) au **strike** `K` ; l'acheteur paie une **prime** |
| Européenne / américaine | exercice à l'échéance seulement / à tout moment avant l'échéance |
| Vanille / exotique | call ou put simple sur un actif / barrière, asiatique, lookback… |
| Payoff | ce que reçoit l'acheteur à l'échéance, **sans** la prime |
| Profit | payoff **moins** la prime |
| Volatilité `σ` | écart-type annualisé des rendements : l'incertitude sur le prix futur |

### 3.2 Le prix forward et la stratégie d'arbitrage

Pour un actif sans revenu : **`F0 = S0·e^(rT)`**. La justification est une stratégie : emprunter `S0`, acheter l'actif, vendre le forward. À l'échéance, on livre l'actif, on reçoit `F0` et on rembourse `S0·e^(rT)`. Si `F0` coté dépasse `S0·e^(rT)`, ce gain est positif sans risque, donc le prix ne peut pas rester là.

| Situation | Aujourd'hui | À l'échéance | Gain |
|---|---|---|---|
| Forward coté **trop cher** (`F_coté > S0·e^(rT)`) | emprunter `S0`, acheter l'actif, **vendre** le forward | livrer l'actif, recevoir `F_coté`, rembourser `S0·e^(rT)` | `F_coté − S0·e^(rT)` |
| Forward coté **trop bon marché** | vendre l'actif à découvert, placer `S0`, **acheter** le forward | recevoir `S0·e^(rT)`, payer `F_coté`, restituer l'actif | `S0·e^(rT) − F_coté` |

Exemple du cours (exercice 2.1) : `S0 = 80`, `r = 4 %`, `T = 0,5` donne `F0 = 81,62 €` ; coté 82 €, le gain d'arbitrage est 0,38 €.

**Valeur d'un forward en cours de vie** (pour l'acheteur) : `Vt = St − F0·e^(−r(T−t))`. Elle vaut zéro à la signature, peut devenir positive ou négative, et tend vers `S_T − F0` à l'échéance. Le vendeur détient `−Vt`. Exercice 2.7 : `F0 = 100`, `St = 108`, `r = 4 %`, six mois restants donne `Vt = 9,98 €`.

**Forward contre futures** : même prix si le taux est constant (cours §2.3.4). La différence est institutionnelle : risque de contrepartie, standardisation, liquidité, appels de marge.

## 4. Les options : payoff, parité, ce qui fait leur valeur

### 4.1 Payoff, profit et seuils de rentabilité

| Position | Payoff à l'échéance | Profit | Seuil de rentabilité | Perte maximale |
|---|---|---|---|---|
| Achat de call | `max(S_T − K, 0)` | payoff − prime | `K + prime` | la prime |
| Achat de put | `max(K − S_T, 0)` | payoff − prime | `K − prime` | la prime |
| Vente de call | `−max(S_T − K, 0)` | prime − payoff | `K + prime` | **illimitée** |
| Vente de put | `−max(K − S_T, 0)` | prime − payoff | `K − prime` | `K − prime` |

Le **straddle** (TD 2, exercice 5) consiste à acheter un call et un put de même strike. Il gagne si le prix s'écarte fortement de `K` dans un sens ou dans l'autre : c'est un pari sur la **volatilité**, pas sur la direction. Ses deux seuils sont `K ± (prime du call + prime du put)`.

**Moneyness** : un call est *dans la monnaie* si `S > K`, *à la monnaie* si `S ≈ K`, *hors de la monnaie* si `S < K` (l'inverse pour un put).

### 4.2 La parité call-put : la relation qui relie tout

Pour des options européennes de même `K` et même `T` : **`C − P = S0 − K·e^(−rT)`**. Acheter un call et vendre un put donne à l'échéance `S_T − K` dans tous les cas, exactement comme détenir l'action financée par un emprunt de `K·e^(−rT)`. Les deux coûtent donc la même chose. C'est `K` qu'on actualise, pas `S0` (cinquième piège du notebook).

Usages : déduire le prix du put à partir du call (exercice 2.3 : `S0 = K = 60`, `r = 3 %`, `T = 0,5`, `C = 4` donne `P = 3,11 €`) ; détecter un arbitrage quand l'écart `(C − P) − (S0 − K·e^(−rT))` n'est pas nul (TD 2, exercice 4) ; **tester un pricer**. Notre projet vérifie la parité sur 243 combinaisons de paramètres.

### 4.3 Ce qui fait la valeur d'une option avant l'échéance

Valeur = **valeur intrinsèque** (ce que rapporterait un exercice immédiat) + **valeur temps** (la possibilité que cela s'améliore d'ici l'échéance). La valeur temps augmente avec la volatilité et la durée restante. Pour l'acheteur, la volatilité est une bonne nouvelle, car la perte est bornée à la prime et le gain ne l'est pas. Sens de variation d'un call européen : il croît avec `S`, `σ`, `T` et `r`, il décroît avec `K`. Le put croît avec `K` et `σ`, décroît avec `S` et `r` ; l'effet de `T` sur un put européen est ambigu.

## 5. Le modèle binomial (TD 3) : la réplication rendue visible

### 5.1 Une période

L'action vaut `S0` et passe à `S0·u` ou `S0·d`. On construit un portefeuille de `Δ` actions et d'un montant `B` placé sans risque qui donne exactement l'option dans les deux états :

| Grandeur | Formule |
|---|---|
| Probabilité risque-neutre | `q = (e^(rΔt) − d) / (u − d)`, avec la condition de non-arbitrage `d < e^(rΔt) < u` |
| Prix | `V0 = e^(−rΔt)·[q·Vu + (1 − q)·Vd]` |
| Delta de réplication | `Δ = (Vu − Vd) / (S0·u − S0·d)` |
| Montant sans risque | `B = e^(−rΔt)·(Vu − Δ·S0·u)` ; contrôle : `V0 = Δ·S0 + B` |

Exemple du notebook : `S0 = 100`, `u = 1,2`, `d = 0,9`, `r = 5 %`, `Δt = 1`, call `K = 100` donne `q = 0,5042`, `V0 = 9,59`, `Δ = 0,667`, `B = −57,07`. Le `B` négatif signifie qu'on **emprunte** pour acheter les actions.

### 5.2 Plusieurs périodes, CRR et options américaines

À `N` pas, `Δt = T/N` (dans `q` **et** dans l'actualisation). On part des payoffs terminaux et on remonte l'arbre (induction rétrograde). Le calibrage de **Cox-Ross-Rubinstein** relie l'arbre à la volatilité : `u = e^(σ√Δt)`, `d = 1/u`. Pour une option **américaine**, chaque nœud prend `max(valeur de continuation, exercice immédiat)`. Un put américain vaut donc au moins autant que le put européen. Pour un call américain sans dividende, l'exercice anticipé n'est jamais optimal.

### 5.3 Convergence vers Black-Scholes

Quand `N` augmente, le prix CRR converge vers celui de Black-Scholes. Recalcul avec `S0 = K = 100`, `T = 1`, `r = 5 %`, `σ = 20 %` :

| `N` | Call européen CRR | Put européen CRR | Put américain CRR |
|---|---|---|---|
| 1 | 12,1623 | 7,2852 | 7,2852 |
| 10 | 10,2534 | 5,3764 | 6,0043 |
| 100 | 10,4306 | 5,5536 | 6,0824 |
| 1 000 | 10,4486 | 5,5715 | 6,0896 |
| Black-Scholes | **10,4506** | **5,5735** | pas de formule fermée |

L'écart d'environ 0,52 entre put américain et put européen est la **prime d'exercice anticipé**. Le Projet 4 (binomial et options américaines) en fait son sujet et compare son arbre à notre `bs_price`.

## 6. Black-Scholes, Grecques et méthodes voisines

### 6.1 Black-Scholes : le prolongement continu de l'arbre

Black-Scholes suppose un prix log-normal (mouvement brownien géométrique), `σ` et `r` constants, aucun frais ni dividende, un marché continu sans arbitrage. Il donne `C = S·N(d1) − K·e^(−rT)·N(d2)` ; le put suit par parité. `N(d2)` est la probabilité risque-neutre d'exercice, `N(d1)` le Delta du call. Le détail (formules, cinq Grecques, preuves, valeurs de référence) est dans [`COMPRENDRE.md`](COMPRENDRE.md) §3 à §5.

### 6.2 Les Grecques : des sensibilités qui servent à couvrir

| Grecque | Sensibilité à | Usage métier |
|---|---|---|
| Delta | `S` | nombre d'actions pour couvrir l'option (Projet 6) |
| Gamma | `S` (dérivée seconde) | vitesse à laquelle la couverture se périme ; coût du réajustement |
| Vega | `σ` | exposition à la volatilité ; base de la méthode de Newton du Projet 7 |
| Theta | temps | érosion quotidienne de la valeur temps |
| Rho | `r` | exposition aux taux |

### 6.3 Les méthodes que les autres projets ajoutent (*hors supports*)

**Monte-Carlo** (Projet 5) : simuler `S_T = S0·exp((r − σ²/2)T + σ√T·Z)`, `Z` normale centrée réduite, puis prix = `e^(−rT)` × moyenne des payoffs. L'erreur décroît en `1/√n` ; intervalle de confiance à 95 % : moyenne ± 1,96·écart-type/√n. Seule méthode simple pour les payoffs qui dépendent du chemin (option asiatique). Une **variable de contrôle** réduit la variance en corrigeant par un produit au prix connu.

**Couverture en Delta** (Projet 6) : vendre une option et détenir `Δ` actions, réajusté périodiquement. Le P&L de la couverture dépend de l'écart entre volatilité réalisée et volatilité implicite, pondéré par le Gamma : c'est le *gamma scalping*. Les frais de transaction rendent un réajustement continu impossible.

**Volatilité implicite** (Projet 7) : le `σ` qui, injecté dans Black-Scholes, redonne le prix de marché. Méthode de Newton : `σ ← σ − (BS(σ) − C_marché)/Vega(σ)`. Recalcul : partant de `σ = 0,5` pour retrouver `C = 10,4506`, on obtient 0,1977 puis 0,200001 puis 0,2000, soit trois itérations. Tracée en fonction de `K`, elle n'est pas plate : c'est le **smile**, preuve que l'hypothèse de `σ` constante est fausse.

**Deep Hedging** (Projet 9) : un réseau de neurones choisit la quantité de couverture à chaque date pour minimiser le risque du P&L couvert, frais inclus. C'est la version apprise de la couverture en Delta.

## 7. La volatilité : mesurer, prévoir, impliquer

| Mesure | Définition | Où on la rencontre |
|---|---|---|
| Historique | `std(r_t) × √252` avec `r_t = ln(S_t / S_{t−1})` | Projet 1 (notre σ d'entrée) |
| Réalisée glissante | même calcul sur une fenêtre courte (5 jours, 21 jours) | cible du LSTM du Projet 1 |
| EWMA (*hors supports*) | `σ²_t = λ·σ²_{t−1} + (1 − λ)·r²_{t−1}`, `λ = 0,94` (RiskMetrics) | référence de comparaison |
| GARCH(1,1) (*hors supports*) | `σ²_t = ω + α·r²_{t−1} + β·σ²_{t−1}`, stationnaire si `α + β < 1`, variance de long terme `ω/(1 − α − β)` | Projet 8 (MASI, MADEX), Projet 10 (DCC) |
| Implicite | extraite des prix d'options par inversion de Black-Scholes | Projet 7 |

Le fait stylisé clé est le **regroupement de la volatilité** (*clustering*) : les fortes variations suivent les fortes variations. Pour cette raison, la volatilité est prévisible alors que les rendements le sont très peu. GARCH formalise ce regroupement ; le LSTM tente de l'apprendre. Une IA de volatilité se juge **contre ces références** : persistance, EWMA, GARCH. Un LSTM qui ne bat pas la persistance n'apporte rien, et le dire fait partie du résultat.

**Convention d'annualisation** : `√252` (jours de bourse) pour la volatilité, `T` en jours calendaires sur 365 pour la maturité. Le décalage est assumé et doit pouvoir s'expliquer.

## 8. La théorie du portefeuille et le CAPM

### 8.1 Rentabilité, risque, diversification

Rentabilité d'un actif sur une période : `R = (P1 − P0 + D) / P0`. Risque : écart-type des rentabilités, avec `n − 1` au dénominateur. Pour deux actifs de poids `w1` et `w2 = 1 − w1` :

`E(Rp) = w1·E(R1) + w2·E(R2)` et `σp² = w1²σ1² + w2²σ2² + 2·w1·w2·ρ·σ1·σ2`.

La rentabilité est une moyenne pondérée, **le risque non**, sauf si `ρ = 1`. C'est tout l'intérêt de la diversification. Avec `ρ = 1`, aucun gain ; avec `ρ < 1`, `σp` passe sous la moyenne pondérée des risques ; avec `ρ = −1`, le risque peut être annulé (exercice 2.6 : 15 %, 10,61 %, 0 %).

**Portefeuille de variance minimale** (TD 2, exercice 7) : `wA* = (σB² − ρ·σA·σB) / (σA² + σB² − 2ρ·σA·σB)`. Quand la vente à découvert est interdite et que la formule sort de [0, 1], on prend la borne. Recalcul avec les données de l'exercice 6 (`σA = 25 %`, `σB = 12 %`, `ρ = 0,4`) : `wA* = 0,0454`.

**Frontière efficiente** : la branche **haute** de la courbe (σp, E(Rp)), c'est-à-dire la rentabilité maximale pour chaque niveau de risque. Sous le point de variance minimale, on trouve un portefeuille plus rentable au même risque : aucun investisseur rationnel ne s'y place.

### 8.2 N actifs : l'écriture matricielle du Projet 3

Avec un vecteur de poids `w`, un vecteur de rentabilités attendues `μ` et une matrice de covariance `Σ` : `E(Rp) = wᵀμ`, `σp² = wᵀΣw`. Markowitz minimise `wᵀΣw` sous les contraintes `wᵀμ = cible` et `wᵀ1 = 1`. Le **ratio de Sharpe** `(Rp − Rf)/σp` mesure la rentabilité par unité de risque ; le portefeuille qui le maximise est le **portefeuille tangent**. La **droite de marché des capitaux** relie l'actif sans risque à ce portefeuille (TP 2, travail demandé n° 3).

### 8.3 Le CAPM : quel risque est rémunéré

Le risque d'un actif se décompose en **risque spécifique**, éliminable par diversification et donc non rémunéré, et **risque systématique**, lié au marché, mesuré par `β = Cov(Ri, Rm) / Var(Rm)`.

| Formule | Lecture |
|---|---|
| `E(Ri) = Rf + β·(E(Rm) − Rf)` | rentabilité exigée pour le risque de marché porté |
| `E(Rm) − Rf` | prime de risque du marché |
| `α = rentabilité offerte − rentabilité CAPM` | `α < 0` : l'actif rapporte moins qu'exigé, il est **surévalué** ; `α > 0` : sous-évalué |

Exemple du cours (exercice 2.5) : `Rf = 3 %`, `E(Rm) = 8 %`, `β = 1,4` donne 10 %. TD 2, exercice 8 : `Cov = 0,0042` et `Var = 0,0030` donnent `β = 1,4`.

## 9. Les dix projets intégrateurs : une carte de la matière

Le guide indique que les groupes 4, 5, 6, 7 et 9 réutilisent `bs_price` et `greeks`. L'usage précis indiqué dans la dernière colonne est déduit de leur sujet, pas écrit dans le guide.

| Projet | Sujet | Notions mobilisées | Lien avec le Projet 1 |
|---|---|---|---|
| 1 | Pricer d'options et Grecques | Black-Scholes, Grecques, volatilité historique, LSTM | **notre projet** ; fournit `bs_price` et `greeks` |
| 2 | Portefeuille obligataire | taux actuariel (YTM), duration de Macaulay, bootstrap, zéro-coupon, lissage de courbe | aucun |
| 3 | Optimisation Markowitz | covariance, frontière efficiente, CAPM, Sharpe | aucun |
| 4 | Binomial et options américaines | CRR, risque-neutre, exercice anticipé, *deep pricing* | compare son arbre à notre Black-Scholes |
| 5 | Monte-Carlo, options exotiques | GBM, option asiatique, intervalle de confiance, variable de contrôle | contrôle par notre prix européen |
| 6 | Couverture en Delta | Delta, Gamma, Theta, P&L, Random Forest | utilise nos Grecques |
| 7 | Volatilité implicite et smile | Newton-Raphson, smile, surface, réseau de neurones | inverse notre `bs_price` avec notre Vega |
| 8 | Volatilité du MASI et du MADEX | GARCH(1,1), clustering, `arch`, LSTM | même problème de prévision que notre LSTM |
| 9 | Deep Hedging | PyTorch, frais de transaction, minimisation de variance | notre Delta comme référence |
| 10 | Risque systémique (CoVaR) | CoVaR, DCC-GARCH, corrélation dynamique, autoencodeur | aucun |

Deux conséquences pour nous. Nos **conventions d'unités** (`CONVENTIONS.md`) s'imposent à cinq groupes : une erreur chez nous se propage. Et les questions de soutenance des autres groupes portent souvent sur des notions que nous devons aussi maîtriser : parité, Delta, volatilité.

**Obligations, rappel de base (*hors supports*, chapitre 1 non fourni)** : prix = somme des flux actualisés au taux actuariel `y` ; **duration de Macaulay** = moyenne des dates de flux pondérée par leur valeur actualisée ; duration modifiée `D/(1 + y)` ; approximation `ΔP/P ≈ −D_mod·Δy`. Le **bootstrap** extrait les taux zéro-coupon maturité par maturité à partir des obligations à coupons.

## 10. Odoo : comment une formule devient un module d'entreprise

### 10.1 L'architecture

Odoo 17 Community tourne dans **Docker** : un conteneur `odoo:17.0` (serveur web Python, port 8069) et un conteneur `postgres:15` (base de données). Le dossier `addons/` de la machine est monté dans le conteneur ; Odoo y trouve les modules. Après tout changement de code Python ou XML, on **met à jour le module** (`-u cours_derives`) ; après l'ajout d'un nouveau dossier de module, on redémarre (`docker compose restart web`).

### 10.2 L'anatomie d'un module (`cours_derives`, TP 0)

| Fichier | Rôle |
|---|---|
| `__manifest__.py` | nom, version, dépendances (`depends`), fichiers XML et CSV chargés (`data`) |
| `__init__.py`, `models/__init__.py` | importent les fichiers Python des modèles |
| `models/forward.py`, `models/option.py`… | classes `models.Model` : `_name` (nom technique), champs, méthodes |
| `security/ir.model.access.csv` | droits de lecture, écriture, création, suppression par modèle |
| `views/*.xml` | vues formulaire, liste (`<tree>` en Odoo 17), graphique, pivot ; actions ; menus |
| `data/demo.xml` | enregistrements de démonstration |
| `tests/` | tests `TransactionCase`, lancés par `--test-tags` |

### 10.3 Les mécanismes de l'ORM à comprendre

L'**ORM** (Object-Relational Mapping) traduit chaque classe en table PostgreSQL et chaque champ en colonne. `_name = "cours.option"` crée la table ; `_inherit = "cours.option"` **étend** le modèle existant sans le recopier. C'est exactement ce que fait notre projet.

Un **champ calculé** (`compute="_compute_x"`) est rempli par une méthode. `@api.depends("a", "b")` déclare de quels champs il dépend : sans lui, un champ stocké ne se recalcule pas quand `a` change (question 2 du TP). `store=True` l'écrit en base : sans stockage, il est recalculé à chaque lecture et ne peut servir ni au tri ni au regroupement dans les vues liste, graphique et pivot (question 3 du TP). `@api.constrains` refuse un enregistrement incohérent (`t > T`, `ρ` hors de [−1, 1] : exercices A et D du TP).

`ir.model.access.csv` est indispensable : sans ligne de droits, Odoo signale que le modèle n'a pas de règle d'accès et l'interface en refuse l'accès (question 4 du TP). Un **bouton** de type `object` appelle une méthode Python du modèle (notre `action_calculer`). Les **vues graphique et pivot agrègent des enregistrements** ; elles ne tracent pas une fonction comme `Delta(S)`, d'où le modèle de points prévu dans notre plan.

### 10.4 Les tests côté Odoo

`TransactionCase` crée des enregistrements dans une transaction annulée à la fin de chaque test. On les décore de `@tagged("post_install", "-at_install")` et on les lance par `docker compose run --rm web odoo -d mabase -u cours_derives --test-tags /cours_derives --stop-after-init`. Le TP demande un test par exercice (forward 9,98 ; arbitrage 0,38) et de **casser volontairement une formule** (`−r` en `+r`) pour vérifier que le test échoue. Un test qui ne peut pas échouer ne prouve rien.

## 11. L'IA en finance de marché : ce qui est exigé et ce qui est jugé

Le cours (§2.8.3) cite quatre usages : prévoir la volatilité (GARCH, LSTM), calibrer un modèle (`σ` implicite par réseau de neurones), optimiser un portefeuille (apprentissage par renforcement), détecter des arbitrages ou anomalies. Le guide applique des règles de méthode communes à tous les projets :

| Règle | Raison |
|---|---|
| Découpage **chronologique** (ex. 70 / 15 / 15), jamais aléatoire | un découpage aléatoire laisse le modèle voir le futur |
| Normalisation apprise sur le **train seul** | sinon la moyenne et l'écart-type du test fuient dans l'apprentissage |
| Comparer à une **référence simple** (persistance, EWMA, GARCH, Black-Scholes) | un modèle complexe ne vaut que par son gain sur le simple |
| Vérifier que la cible ne recouvre pas l'entrée | sinon le modèle « prédit » ce qu'il voit déjà (piège de notre LSTM) |
| Entraîner hors d'Odoo, n'y faire que l'**inférence** | l'image Odoo n'embarque ni TensorFlow ni PyTorch |
| Rapporter honnêtement un échec | la soutenance évalue la démarche, pas seulement le score |

## 12. Formulaire condensé : la feuille à réécrire de mémoire

| Thème | Formules |
|---|---|
| Actualisation | capitaliser `e^(rT)` ; actualiser `e^(−rT)` |
| Forward | `F0 = S0·e^(rT)` ; `Vt = St − F0·e^(−r(T−t))` |
| Options | call `max(S_T − K, 0)` ; put `max(K − S_T, 0)` ; profit = payoff − prime ; seuils `K ± prime` |
| Parité | `C − P = S0 − K·e^(−rT)` |
| Binomial | `q = (e^(rΔt) − d)/(u − d)` ; `V0 = e^(−rΔt)[qVu + (1 − q)Vd]` ; `Δ = (Vu − Vd)/(Su − Sd)` ; CRR `u = e^(σ√Δt)`, `d = 1/u` |
| Black-Scholes | `d1 = [ln(S/K) + (r + σ²/2)T]/(σ√T)` ; `d2 = d1 − σ√T` ; `C = S·N(d1) − K·e^(−rT)·N(d2)` |
| Volatilité | `r_t = ln(S_t/S_{t−1})` ; `σ = std(r_t)·√252` |
| Deux actifs | `E(Rp) = w1E(R1) + w2E(R2)` ; `σp² = w1²σ1² + w2²σ2² + 2w1w2ρσ1σ2` |
| Variance minimale | `wA* = (σB² − ρσAσB)/(σA² + σB² − 2ρσAσB)` |
| CAPM | `E(Ri) = Rf + β(E(Rm) − Rf)` ; `β = Cov(Ri, Rm)/Var(Rm)` ; Sharpe `(Rp − Rf)/σp` |
| Odoo | `_inherit` ; `compute` + `@api.depends` + `store=True` ; `@api.constrains` ; `ir.model.access.csv` ; vue + action + menu |

## 13. Les neuf pièges d'examen du notebook de révision

Oublier l'exponentielle (`S0·e^(rT)`, pas `S0(1 + rT)`). Se tromper de sens d'arbitrage : un forward trop cher se **vend** et l'actif s'**achète**. Confondre payoff et profit. Oublier que la perte du vendeur de call est **illimitée**. Actualiser `S0` au lieu de `K` dans la parité. Croire que `ρ = 1` diversifie. Prendre la branche basse pour la frontière efficiente. Juger sous-évalué un actif qui rapporte **moins** que le CAPM : il est **surévalué**. Confondre forward (OTC, sur mesure) et futures (bourse, standardisé, appels de marge). Le TD 3 ajoute deux pièges : `Δt = T/N` partout, et `q` n'est pas la probabilité réelle.

## 14. Parcours de travail conseillé

Lire les sections 2 à 4 avant de refaire le TD 2, puis la section 5 avant le TD 3. Ensuite, la section 10 en ayant le TP Odoo ouvert, puis `COMPRENDRE.md` pour le projet. Pour chaque formule du formulaire, refaire l'exemple chiffré du cours à la main, puis le vérifier en Python avec les fonctions du TP (`prix_forward`, `put_par_parite`, `payoff_call`, `payoff_put`) ou avec `src/pricing.py`. La compréhension est acquise quand on peut **justifier une formule par une stratégie de réplication ou d'arbitrage**, pas seulement la réciter. C'est ce que vérifient le professeur en mini-compte rendu et le jury en soutenance.
