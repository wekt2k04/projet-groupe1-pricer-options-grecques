{
    'name': 'Cours : produits dérivés et théorie du portefeuille',
    'version': '17.0.1.0.0',
    'summary': 'Forwards, options, portefeuille (Markowitz), CAPM et volatilité',
    'description': """
Module pédagogique du chapitre 2 (ENSA Safi, GIIA) :
 - cours.forward   : prix forward F0 = S0.exp(rT), valeur en cours de vie, signal d'arbitrage
 - cours.option    : payoff, profit, seuil de rentabilité, prix Black-Scholes, statut ITM/ATM/OTM
 - cours.portfolio : valeur totale, payoff total, répartition calls/puts
 - cours.markowitz : portefeuille de deux actifs, variance minimale
 - cours.capm      : rentabilité CAPM, alpha, verdict
 - cours.volatility: volatilité historique, EWMA et prévision (scikit-learn si disponible)
""",
    'category': 'Accounting/Finance',
    'author': 'Cours GIIA - ENSA Safi',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/derives_views.xml',
        'views/portefeuille_views.xml',
        'views/menus.xml',
    ],
    'demo': ['demo/demo.xml'],
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
