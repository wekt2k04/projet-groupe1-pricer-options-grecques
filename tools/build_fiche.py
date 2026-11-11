import pathlib
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle, KeepTogether)

F = "/usr/share/fonts/truetype/dejavu/"
if not pathlib.Path(F).exists():          # Windows / macOS : polices DejaVu fournies avec matplotlib
    import matplotlib
    F = str(pathlib.Path(matplotlib.get_data_path()) / "fonts" / "ttf") + "/"
for n, f in (("DV", "DejaVuSans.ttf"), ("DV-B", "DejaVuSans-Bold.ttf"), ("DV-I", "DejaVuSans-Oblique.ttf"),
             ("DV-BI", "DejaVuSans-BoldOblique.ttf")):
    pdfmetrics.registerFont(TTFont(n, F + f))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-BI")

BLUE = colors.HexColor("#0B3C5D")
S = {
    "t": ParagraphStyle("t", fontName="DV-B", fontSize=16, leading=20, textColor=BLUE, spaceAfter=2),
    "st": ParagraphStyle("st", fontName="DV", fontSize=9, leading=12, textColor=colors.HexColor("#444444"), spaceAfter=1),
    "h": ParagraphStyle("h", fontName="DV-B", fontSize=11.5, leading=15, textColor=BLUE, spaceBefore=9, spaceAfter=3),
    "p": ParagraphStyle("p", fontName="DV", fontSize=9, leading=13, alignment=TA_JUSTIFY, spaceAfter=4),
    "f": ParagraphStyle("f", fontName="DV", fontSize=9.2, leading=14, alignment=1, spaceAfter=2,
                        backColor=colors.HexColor("#F2F6FA"), borderPadding=(3, 3, 3, 3)),
    "c": ParagraphStyle("c", fontName="DV", fontSize=8, leading=10.5),
    "ch": ParagraphStyle("ch", fontName="DV-B", fontSize=8, leading=10.5, textColor=colors.white),
    "r": ParagraphStyle("r", fontName="DV", fontSize=8.3, leading=11.5, leftIndent=10, firstLineIndent=-10, spaceAfter=2),
}


def P(t): return Paragraph(t, S["p"])
def H(t): return Paragraph(t, S["h"])
def FM(t): return Paragraph(t, S["f"])


def table(rows, widths):
    data = [[Paragraph(c, S["ch"] if i == 0 else S["c"]) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * cm for w in widths], repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), BLUE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B8C4CE")),
                           ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F6F8FA")]),
                           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return t


def footer(c, d):
    c.saveState(); c.setFont("DV", 7.5); c.setFillColor(colors.HexColor("#666666"))
    c.drawString(2 * cm, 1.2 * cm, "Groupe 1 · Projet 1 · Fiche de lecture (Phase 0) · Finance des Marchés et ERP")
    c.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {d.page}"); c.restoreState()


st = []
st += [Paragraph("Fiche de lecture — Pricer d'Options &amp; Grecques", S["t"]),
       Paragraph("Groupe 1 · Phase 0 · Black-Scholes, Grecques, volatilité et prévision par LSTM", S["st"]),
       Paragraph("Module Finance des Marchés et ERP — ENSA Safi, 2026-2027 · Membres : Hiba BOULHAIL, Assia SADOUR, "
                 "Fatima-ezzahraa EL ANKOUD, Zineb ELAMRANI, Komla Edem Wilfried TSETSE", S["st"]),
       Spacer(1, 4)]

st += [H("1. Objet de la lecture"),
       P("Avant de coder, nous fixons la théorie dont dépend tout le projet : le prix d'une option européenne par la formule de "
         "Black-Scholes, ses cinq sensibilités (les Grecques), la volatilité comme seul paramètre non observable, et la prévision de "
         "cette volatilité par un réseau LSTM. Notre fonction de prix est réutilisée par cinq autres groupes ; ses hypothèses et "
         "ses unités doivent donc être sans ambiguïté.")]

st += [H("2. Le modèle de Black-Scholes"),
       P("<b>Hypothèses.</b> Le prix du sous-jacent suit un mouvement brownien géométrique (rendements log-normaux) à volatilité σ "
         "constante ; le taux sans risque r est constant ; pas de dividendes, de coûts de transaction ni de taxes ; vente à découvert "
         "autorisée ; négociation continue et absence d'opportunité d'arbitrage ; option européenne, exercée à l'échéance seulement."),
       P("<b>Idée.</b> On peut construire un portefeuille composé de l'actif et de l'option dont le risque disparaît à chaque instant "
         "(couverture dynamique). Un portefeuille sans risque doit rapporter le taux sans risque, ce qui impose à la valeur V(S, t) de "
         "l'option l'équation aux dérivées partielles suivante. Le rendement espéré de l'action n'y figure pas : le prix ne dépend pas "
         "des préférences des investisseurs, ce qui revient à valoriser comme si tout actif rapportait r (mesure risque-neutre)."),
       FM("∂V/∂t + ½·σ²·S²·∂²V/∂S² + r·S·∂V/∂S − r·V = 0"),
       P("Avec la condition terminale max(S − K, 0) pour un call, la solution est fermée :"),
       FM("d<sub>1</sub> = [ ln(S/K) + (r + σ²/2)·T ] / (σ·√T)  ;  d<sub>2</sub> = d<sub>1</sub> − σ·√T"),
       FM("Call = S·N(d<sub>1</sub>) − K·e<super>−rT</super>·N(d<sub>2</sub>)  ;  Put = K·e<super>−rT</super>·N(−d<sub>2</sub>) − S·N(−d<sub>1</sub>)"),
       P("N est la fonction de répartition de la loi normale centrée réduite. N(d<sub>2</sub>) est la probabilité, sous la mesure "
         "risque-neutre, que le call finisse dans la monnaie ; N(d<sub>1</sub>) est le Delta du call, et non une probabilité d'exercice. "
         "L'absence d'arbitrage impose aussi la parité call-put, C − P = S − K·e<super>−rT</super>, que nous utilisons pour valider le code.")]

st += [H("3. Les cinq Grecques"),
       table([["Grecque", "Définition", "Formule (call)", "Lecture"],
              ["Delta", "∂V/∂S", "N(d<sub>1</sub>)", "Variation du prix pour +1 sur le spot ; quantité d'actifs de la couverture."],
              ["Gamma", "∂²V/∂S²", "φ(d<sub>1</sub>) / (S·σ·√T)", "Vitesse de variation du Delta ; identique pour le call et le put."],
              ["Vega", "∂V/∂σ", "S·φ(d<sub>1</sub>)·√T", "Sensibilité à la volatilité ; identique pour le call et le put."],
              ["Theta", "∂V/∂t", "−S·φ(d<sub>1</sub>)·σ / (2√T) − r·K·e<super>−rT</super>·N(d<sub>2</sub>)", "Érosion de la valeur avec le temps."],
              ["Rho", "∂V/∂r", "K·T·e<super>−rT</super>·N(d<sub>2</sub>)", "Sensibilité au taux sans risque."]],
             [2.1, 2.0, 6.2, 6.7]),
       Spacer(1, 3),
       P("φ désigne la densité de la loi normale centrée réduite. Pour le put : Delta = N(d<sub>1</sub>) − 1, Theta = −S·φ(d<sub>1</sub>)·σ/(2√T) "
         "+ r·K·e<super>−rT</super>·N(−d<sub>2</sub>), Rho = −K·T·e<super>−rT</super>·N(−d<sub>2</sub>). Les Grecques vérifient l'équation de "
         "Black-Scholes : Theta + ½σ²S²·Gamma + r·S·Delta − r·V = 0, relation que nos tests contrôlent. Cas de référence "
         "(S = K = 100, T = 1, r = 5 %, σ = 20 %) : call 10,4506 ; put 5,5735 ; Delta du call 0,6368.")]

st += [H("4. La volatilité : historique, implicite, prévue"),
       P("La volatilité historique est l'écart-type des rendements logarithmiques r<sub>t</sub> = ln(S<sub>t</sub>/S<sub>t−1</sub>), annualisé par "
         "√252. La volatilité implicite est celle qui, injectée dans Black-Scholes, restitue le prix de marché ; son évolution avec le "
         "strike (le smile) montre que le modèle n'est pas exact et qu'il sert de « langage de cotation ». Notre projet utilise la "
         "volatilité historique et une volatilité prévue par LSTM ; l'inversion en volatilité implicite relève d'un autre groupe.")]

st += [H("5. Prévoir la volatilité par un LSTM"),
       P("Le LSTM (Hochreiter et Schmidhuber, 1997) est un réseau récurrent à cellules à mémoire et à portes, conçu pour apprendre des "
         "dépendances longues dans une série. Nous l'alimentons avec des fenêtres glissantes de 30 valeurs de volatilité réalisée pour "
         "prédire la valeur suivante, avec normalisation apprise sur l'échantillon d'entraînement seul et découpage chronologique "
         "70 / 15 / 15, sans mélange aléatoire."),
       P("<b>Point de vigilance.</b> Une volatilité glissante sur 5 jours partage 4 de ses 5 rendements avec celle du jour précédent : "
         "la règle « demain = aujourd'hui » obtient alors un score élevé par construction. Pour que le LSTM soit jugé honnêtement, "
         "nous le comparons à trois références : la persistance, la moyenne mobile exponentielle de RiskMetrics (λ = 0,94) et un "
         "GARCH(1,1) (Bollerslev, 1986), avec une cible tournée vers l'avenir et des mesures RMSE et QLIKE. Enfin, Black-Scholes "
         "requiert la volatilité moyenne jusqu'à l'échéance, alors que le LSTM prévoit celle du lendemain : la prévision devra "
         "être agrégée sur la maturité avant d'être injectée dans le prix.")]

st += [H("6. Lien avec le TP 0 : ce que nous modifions"),
       P("Le module <i>cours_derives</i> du TP 0 contient déjà le modèle <i>cours.option</i> : champs saisis type, position, quantity, "
         "S0, S_T, K, premium, r, T, sigma ; champs calculés payoff, profit, break_even, moneyness et bs_price. Nous ne touchons pas à "
         "ce fichier : <i>models/option_greeks.py</i> l'étend par <i>_inherit = 'cours.option'</i> et ajoute greeks_delta, greeks_gamma, "
         "greeks_vega, greeks_theta et greeks_rho (compute, store=True, @api.depends('type', 'S0', 'K', 'r', 'T', 'sigma')), "
         "sigma_lstm et bs_price_lstm. <i>cours.portfolio</i> reçoit la somme signée des Grecques de ses options (delta_total) ; "
         "deux modèles nouveaux stockent les séries de volatilité et les prévisions (voir le schéma de base de données). "
         "Les noms du TP 0 sont conservés : aucun doublon spot/S0 ou strike/K.")]

st += [H("7. Algorithme de calcul (Python)"),
       P("(1) Télécharger 2 ans de cours de clôture ajustés (yfinance, AAPL ; repli CSV). (2) Calculer r<sub>t</sub> = ln(S<sub>t</sub>/S<sub>t−1</sub>) "
         "puis σ = écart-type(r<sub>t</sub>)·√252. (3) Calculer d<sub>1</sub>, d<sub>2</sub>, le prix (bs_price) et les Grecques (greeks), avec "
         "N(x) = ½·(1 + erf(x/√2)) pour se passer de SciPy dans Odoo ; si T = 0 ou σ = 0, renvoyer la valeur intrinsèque sans "
         "division par zéro. (4) Valider par pytest : parité call-put, différences finies, équation de Black-Scholes. "
         "(5) Appeler ces fonctions dans _compute_greeks. (6) Entraîner le LSTM hors d'Odoo, le comparer aux trois références, "
         "agréger sa prévision sur la maturité et en déduire bs_price_lstm. Questions ouvertes : source du taux r, historique de "
         "10 ans pour le LSTM, noms à aligner avec les groupes 4 et 7, affichage de Delta(S).")]

refs = ["Black, F. et Scholes, M. (1973). The Pricing of Options and Corporate Liabilities. <i>Journal of Political Economy</i>, 81(3), 637-654.",
        "Hull, J. C. <i>Options, Futures and Other Derivatives</i>. Pearson.",
        "Bollerslev, T. (1986). Generalized Autoregressive Conditional Heteroskedasticity. <i>Journal of Econometrics</i>, 31(3), 307-327.",
        "Hochreiter, S. et Schmidhuber, J. (1997). Long Short-Term Memory. <i>Neural Computation</i>, 9(8), 1735-1780.",
        "J.P. Morgan / Reuters (1996). <i>RiskMetrics — Technical Document</i>, 4<super>e</super> éd.",
        "ENSA Safi, cours <i>Produits dérivés et théorie du portefeuille</i>, chapitre 2, et guide des projets intégrateurs."]
st += [KeepTogether([H("8. Références")] + [Paragraph(f"[{i}] {r}", S["r"]) for i, r in enumerate(refs, 1)])]

out = str(pathlib.Path(__file__).resolve().parent.parent / "docs" / "fiche_lecture.pdf")
SimpleDocTemplate(out, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=2 * cm,
                  title="Fiche de lecture - Groupe 1 - Pricer d'Options et Grecques", author="").build(
    st, onFirstPage=footer, onLaterPages=footer)
print("ok", out)
