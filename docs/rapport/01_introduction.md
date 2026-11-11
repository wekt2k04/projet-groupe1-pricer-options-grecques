# 1. Introduction

Le Projet 1 du module Finance des Marchés et ERP construit un outil qui valorise une option européenne par le modèle de Black-Scholes, calcule ses cinq sensibilités (les Grecques), les met à disposition dans Odoo 17 en étendant le modèle `cours.option` du module `cours_derives` (TP 0), et prévoit la volatilité, seule entrée non observable du modèle, à l'aide d'un réseau LSTM.

C'est le projet socle du module : les groupes 4, 5, 6, 7 et 9 réutilisent nos fonctions `bs_price` et `greeks`. Cette position impose deux exigences qui structurent tout le rapport : des conventions d'unités communes, figées dans `CONVENTIONS.md`, et une preuve que le calcul est juste, apportée par trois vérifications indépendantes (section 3).

Le rapport suit la chaîne de l'outil : la théorie (section 2), les données et le code Python (section 3), l'intégration Odoo (section 4), l'IA (section 5), les tests (section 6), puis la conduite du projet, le Gantt prévu contre réalisé et les limites (section 7).
