import pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

OUT = str(pathlib.Path(__file__).resolve().parent.parent / "docs") + "/"
DATES = ["11/11", "18/11", "25/11", "02/12", "09/12", "16/12", "23/12"]   # indicatif : une séance par semaine
PH = {"Cadrage": "#0072B2", "Python": "#009E73", "Odoo": "#E69F00", "IA": "#CC79A7",
      "Intégration": "#56B4E9", "Rapport": "#7F7F7F"}
# (tâche, phase, rôle, début S, fin S)
T = [
    ("Fiche de lecture théorique", "Cadrage", "Chef de projet", 1, 1),
    ("Dépôt GitHub, Docker, conventions", "Cadrage", "Qualité & intégration", 1, 1),
    ("Schéma de base de données", "Cadrage", "Dév. Odoo", 1, 1),
    ("Gantt prévisionnel", "Cadrage", "Chef de projet", 1, 1),
    ("Données AAPL et volatilité historique", "Python", "Quant / Data", 1, 2),
    ("bs_price et greeks", "Python", "Quant / Data", 1, 2),
    ("Tests pytest (parité, différences finies)", "Python", "Qualité & intégration", 1, 2),
    ("Notebooks de validation et graphiques", "Python", "Quant / Data", 2, 2),
    ("Extension de cours.option (champs, calcul)", "Odoo", "Dév. Odoo", 3, 3),
    ("Vues formulaire, liste, bouton Calculer", "Odoo", "Dév. Odoo", 3, 4),
    ("Vue graphique Delta(S)", "Odoo", "Dév. Odoo", 4, 4),
    ("Données LSTM, cible, références", "IA", "Ingénieur IA", 3, 3),
    ("Entraînement et évaluation du LSTM", "IA", "Ingénieur IA", 4, 4),
    ("Export du modèle, inférence dans Odoo", "IA", "Ingénieur IA", 5, 5),
    ("Bouton Odoo : calcul + IA, tests Odoo", "Intégration", "Qualité & intégration", 5, 5),
    ("Prix avec σ historique vs σ prédite", "Intégration", "Dév. Odoo", 5, 5),
    ("Gantt mis à jour (mi-parcours)", "Rapport", "Chef de projet", 4, 4),
    ("Rédaction du rapport (80 % en S6)", "Rapport", "Chef de projet", 5, 6),
    ("Module finalisé, code zippé", "Intégration", "Qualité & intégration", 6, 6),
    ("Démonstration : préparation", "Rapport", "Tous", 6, 7),
    ("Gantt réalisé + rapport final", "Rapport", "Chef de projet", 7, 7),
]
# Responsables proposés (à valider en séance) ; rotation obligatoire des rôles à la fin de la S4
R1 = {"Chef de projet": "Wilfried", "Quant / Data": "Assia", "Dév. Odoo": "Fatima-ezzahraa",
      "Ingénieur IA": "Hiba", "Qualité & intégration": "Zineb", "Tous": "Tous"}
R2 = {"Chef de projet": "Zineb", "Quant / Data": "Wilfried", "Dév. Odoo": "Hiba",
      "Ingénieur IA": "Assia", "Qualité & intégration": "Fatima-ezzahraa", "Tous": "Tous"}


def who(role, start):
    return (R1 if start <= 4 else R2)[role]


# un mini-compte rendu chaque semaine, plus ces jalons
MILESTONES = [(1, "Fiche de lecture"), (4, "Rotation des rôles"), (6, "Rapport à 80 %"), (7, "Soutenance")]
EXTRA = dict(MILESTONES)

# ---------- PNG ----------
fig, ax = plt.subplots(figsize=(14, 8.6), dpi=150)
n = len(T)
for i, (name, ph, role, a, b) in enumerate(T):
    y = n - 1 - i
    ax.barh(y, b - a + 1, left=a - 1, height=0.62, color=PH[ph], edgecolor="white")
    ax.text(b + 0.06, y, f"{who(role, a)} ({role})", va="center", fontsize=7.5, color="#555555")
ax.set_yticks(range(n))
ax.set_yticklabels([t[0] for t in T][::-1], fontsize=8.5)
ax.set_xlim(0, 8.3)
ax.set_xticks([w + 0.5 for w in range(7)])
ax.set_xticklabels([f"S{w + 1}\n{DATES[w]}" for w in range(7)], fontsize=8.5)
for w in range(8):
    ax.axvline(w, color="#DDDDDD", lw=0.8, zorder=0)
ax.set_ylim(-2.7, n - 0.3)
for wk in range(1, 8):
    ax.plot(wk - 0.5, -1.2, marker="D", color="#222222", markersize=7, clip_on=False)
    ax.text(wk - 0.5, -1.6, "Mini-CR" + ("\n" + EXTRA[wk] if wk in EXTRA else ""), ha="center", va="top",
            fontsize=7.5, color="#222222")
ax.axvline(4, color="#D55E00", ls="--", lw=1.3, zorder=1)
ax.text(4.05, n - 0.6, "rotation des rôles", color="#D55E00", fontsize=7.5)
ax.tick_params(axis="y", length=0)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.set_title("Gantt prévisionnel — Groupe 1 · Pricer d'Options & Grecques (version S1)", fontsize=12, fontweight="bold",
             loc="left", pad=28)
ax.text(0, 1.018, "Dates indicatives : une séance par semaine à partir du 11/11/2026, à confirmer. "
        "Responsables proposés (rotation à la fin de la S4), à valider en séance. ◆ = jalon.",
        transform=ax.transAxes, fontsize=8, color="#555555")
ax.legend(handles=[Patch(color=c, label=k) for k, c in PH.items()], loc="upper right", ncol=3, fontsize=8, frameon=False,
          bbox_to_anchor=(1.0, 1.0))
fig.tight_layout()
fig.savefig(OUT + "gantt_previsionnel.png")
print("png ok")

# ---------- XLSX (source éditable) ----------
wb = Workbook()
ws = wb.active
ws.title = "Gantt"
ws["A1"] = "Gantt — Groupe 1 · Pricer d'Options & Grecques"
ws["A1"].font = Font(bold=True, size=13)
ws["A2"] = "Renseigner Début/Fin réels (colonnes H, I) et le statut ; les barres se mettent à jour. Dates indicatives : S1 = 11/11/2026."
heads = ["Tâche", "Phase", "Rôle", "Responsable", "Début prévu (S)", "Fin prévue (S)", "Durée (sem.)", "Début réel (S)",
         "Fin réelle (S)", "Statut"]
hr = 4
PL, RL = 12, 20     # première colonne de la grille prévue / réelle (L, T)
thin = Side(style="thin", color="BBBBBB")
hdr_fill = PatternFill("solid", fgColor="0B3C5D")
for c, h in enumerate(heads, 1):
    cell = ws.cell(hr, c, h)
    cell.font = Font(bold=True, color="FFFFFF"); cell.fill = hdr_fill
    cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
ws.cell(hr - 1, PL, "Prévu").font = Font(bold=True)
ws.cell(hr - 1, RL, "Réalisé").font = Font(bold=True)
for w in range(1, 8):
    for base in (PL, RL):
        cell = ws.cell(hr, base + w - 1, w)
        cell.number_format = '"S"0'
        cell.font = Font(bold=True, color="FFFFFF"); cell.fill = hdr_fill
        cell.alignment = Alignment(horizontal="center")
dv = DataValidation(type="list", formula1='"À faire,En cours,Terminé"', allow_blank=True)
ws.add_data_validation(dv)
for i, (name, ph, role, a, b) in enumerate(T):
    r = hr + 1 + i
    for c, v in enumerate([name, ph, role, who(role, a), a, b, f"=F{r}-E{r}+1", None, None, "À faire"], 1):
        cell = ws.cell(r, c, v)
        cell.border = Border(bottom=thin)
        if c in (5, 6, 7, 8, 9):
            cell.alignment = Alignment(horizontal="center")
    ws.cell(r, 2).fill = PatternFill("solid", fgColor=PH[ph].lstrip("#"))
    ws.cell(r, 2).font = Font(color="FFFFFF", bold=True)
    dv.add(ws.cell(r, 10))
    for w in range(1, 8):
        col_p, col_r = get_column_letter(PL + w - 1), get_column_letter(RL + w - 1)
        ws.cell(r, PL + w - 1, f'=IF(AND({col_p}${hr}>=$E{r},{col_p}${hr}<=$F{r}),"■","")')
        ws.cell(r, RL + w - 1, f'=IF(AND($H{r}<>"",{col_r}${hr}>=$H{r},{col_r}${hr}<=$I{r}),"■","")')
last = hr + len(T)
rng_p = f"{get_column_letter(PL)}{hr + 1}:{get_column_letter(PL + 6)}{last}"
rng_r = f"{get_column_letter(RL)}{hr + 1}:{get_column_letter(RL + 6)}{last}"
ws.conditional_formatting.add(rng_p, FormulaRule(formula=[f'{get_column_letter(PL)}{hr + 1}="■"'],
                              fill=PatternFill("solid", bgColor="0072B2", fgColor="0072B2"), font=Font(color="0072B2")))
ws.conditional_formatting.add(rng_r, FormulaRule(formula=[f'{get_column_letter(RL)}{hr + 1}="■"'],
                              fill=PatternFill("solid", bgColor="009E73", fgColor="009E73"), font=Font(color="009E73")))
for col, wd in zip("ABCDEFGHIJ", (42, 13, 22, 16, 9, 9, 8, 9, 9, 11)):
    ws.column_dimensions[col].width = wd
ws.column_dimensions["K"].width = 3
for w in range(7):
    ws.column_dimensions[get_column_letter(PL + w)].width = 5
    ws.column_dimensions[get_column_letter(RL + w)].width = 5
ws.row_dimensions[hr].height = 32
ws.freeze_panes = ws.cell(hr + 1, 2)
ws2 = wb.create_sheet("Jalons")
ws2.append(("Semaine", "Jalon"))
for w in range(1, 8):
    ws2.append((f"S{w}", "Mini-compte rendu (10 min)" + (" ; " + EXTRA[w] if w in EXTRA else "")))
ws3 = wb.create_sheet("Rôles")
ws3.append(("Rôle", "S1 à S4", "S5 à S7 (après rotation)"))
for role in R1:
    if role != "Tous":
        ws3.append((role, R1[role], R2[role]))
for col, wd in zip("ABC", (24, 18, 24)):
    ws3.column_dimensions[col].width = wd
ws2.column_dimensions["B"].width = 46
wb.save(OUT + "gantt_source.xlsx")
print("xlsx ok")
