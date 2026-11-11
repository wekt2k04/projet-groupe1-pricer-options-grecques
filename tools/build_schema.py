"""Régénère docs/schema_bdd.png (schéma de base de données, version S1) sans Graphviz : matplotlib seul."""
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams["font.family"] = "DejaVu Sans"
OUT = pathlib.Path(__file__).resolve().parent.parent / "docs" / "schema_bdd.png"
LH = 0.34  # hauteur d'une ligne de texte

# nom -> (x, y_haut, largeur, couleur du titre, titre, [(sous-titre, fond, [lignes])])
BOXES = {
    "option": (0.2, 9.6, 7.4, "#0B3C5D", "cours.option   (TP 0, étendu par _inherit)", [
        ("Existant (TP 0) : conservé, noms gardés", "#EEEEEE", [
            "name · type (call/put) · position (long/short) · quantity · portfolio_id",
            "S0 (prix aujourd'hui) · S_T (prix à l'échéance) · K · premium",
            "r (taux continu) · T (années) · sigma (annualisée)",
            "calculés : payoff · profit · break_even · moneyness · bs_price"]),
        ("Ajouté par le groupe 1 : calculés et stockés", "#E3F4EA", [
            "greeks_delta · greeks_gamma · greeks_vega · greeks_theta · greeks_rho",
            "@api.depends('type', 'S0', 'K', 'r', 'T', 'sigma')",
            "delta_curve (image Delta(S), champ Binary)"]),
        ("Ajouté : IA", "#F7E6F0", [
            "ticker · sigma_lstm · bs_price_lstm (prix avec σ prédite)",
            "prediction_id → cours.vol.prediction",
            "boutons : Calculer · Prédire la volatilité"])]),
    "portfolio": (0.2, 3.3, 7.4, "#0B3C5D", "cours.portfolio   (TP 0, étendu)", [
        ("Existant : option_ids, forward_ids, totaux · Ajouté :", "#FFF3D6", [
            "delta_total · gamma_total · vega_total = Σ signe × quantité × Grecque"])]),
    "pred": (8.6, 9.6, 6.2, "#A64D79", "cours.vol.prediction   (nouveau)", [
        ("", "#FFFFFF", ["ticker · date_prevision · horizon_jours", "vol_predite (annualisée)",
                         "modele : LSTM / EWMA / GARCH / persistance", "rmse_test · qlike_test"])]),
    "serie": (8.6, 5.5, 6.2, "#00795A", "cours.vol.serie   (nouveau, optionnel)", [
        ("", "#FFFFFF", ["ticker · date · close", "rendement (log) · vol_realisee_5j"])]),
    "hors": (8.6, 2.6, 6.2, "#8A8A8A", "Non étendus (TP 0)", [
        ("", "#F4F4F4", ["cours.forward · cours.markowitz · cours.capm",
                         "cours.volatility (vol. historique / EWMA, réutilisable)"])]),
}

fig, ax = plt.subplots(figsize=(15, 10.2), dpi=130)
ax.set_xlim(0, 15); ax.set_ylim(0, 10.6); ax.axis("off")
ax.text(0.2, 10.25, "Schéma de base de données — Groupe 1 · Pricer d'Options & Grecques (version S1, 11/11/2026)",
        fontsize=14, fontweight="bold", color="#0B3C5D")
anchor = {}
for key, (x, y, w, col, title, sections) in BOXES.items():
    top = y
    ax.add_patch(Rectangle((x, y - 0.42), w, 0.42, color=col))
    ax.text(x + 0.12, y - 0.21, title, va="center", fontsize=10.5, fontweight="bold", color="white")
    y -= 0.42
    for sub, bg, lines in sections:
        h = LH * (len(lines) + (1 if sub else 0)) + 0.12
        ax.add_patch(Rectangle((x, y - h), w, h, facecolor=bg, edgecolor="#9AA5AE", lw=0.8))
        yy = y - 0.08
        if sub:
            ax.text(x + 0.12, yy - LH / 2, sub, va="center", fontsize=9, fontweight="bold", color="#222222")
            yy -= LH
        for ln in lines:
            ax.text(x + 0.12, yy - LH / 2, ln, va="center", fontsize=9, color="#222222")
            yy -= LH
        y -= h
    ax.add_patch(Rectangle((x, y), w, top - y, fill=False, edgecolor="#333333", lw=1.2))
    anchor[key] = (x, y, w, top)


def arrow(a, b, label, side_a, side_b, dashed=False, frac=0.5):
    def pt(k, side):
        x, y0, w, y1 = anchor[k]
        return {"r": (x + w, (y0 + y1) / 2), "l": (x, (y0 + y1) / 2), "t": (x + w / 2, y1), "b": (x + w / 2, y0)}[side]
    p, q = pt(a, side_a), pt(b, side_b)
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color="#444444", lw=1.2,
                                                    ls="--" if dashed else "-", shrinkA=2, shrinkB=2))
    ax.text(p[0] + frac * (q[0] - p[0]), p[1] + frac * (q[1] - p[1]) + 0.12, label, ha="center", fontsize=8.5, color="#444444",
            bbox=dict(fc="white", ec="none", pad=1))


arrow("portfolio", "option", "One2many option_ids (TP 0)", "t", "b")
arrow("option", "pred", "Many2one\nprediction_id", "r", "l", frac=0.45)
arrow("serie", "pred", "même ticker : entrée du LSTM", "t", "b", dashed=True)
arrow("serie", "option", "même ticker : σ historique", "l", "r", dashed=True)
ax.text(0.2, 0.25, "Noms de champs : ceux du module réel du TP 0 (pas de spot / strike / maturite / taux / volatilite, "
        "qui feraient doublon). Voir CONVENTIONS.md.", fontsize=9, color="#555555")
fig.savefig(OUT, bbox_inches="tight")
print("ok", OUT)
