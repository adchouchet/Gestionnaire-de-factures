AllToo - Système de Gestion de Facturation

Voici le rendu Test pour ALLTOO. Cette application est une solution pour la gestion commerciale, le suivi des stocks et la génération automatisée de factures professionnelles.
:clipboard: Présentation du Projet

Mon application est conçue pour offrir une expérience utilisateur. L'application intègre une gestion dynamique des produits, un suivi client rigoureux et un tableau de bord analytique en temps réel.
:sparkles: Fonctionnalités Principales
:briefcase: Gestion Commerciale

    Base de données Produits : Gestion complète (CRUD) avec suivi des stocks et alertes de rupture.
    Gestion CRM : Module dédié à la gestion des clients pour un suivi personnalisé.
    Facturation Avancée : Création de factures avec sélection multiple de produits, calcul automatique de la TVA et déduction automatique du stock.

:bar_chart: Analyse & Reporting

    Tableau de Bord : Vue d'ensemble des indicateurs clés (volume de factures, nombre de clients).
    Alertes Stock : Notification visuelle des produits en stock critique.
    Exports PDF : Génération instantanée de factures professionnelles au format PDF prêtes à l'envoi.

:art: Expérience Utilisateur

    Interface Premium : Design moderne, épuré et entièrement responsive.
    Dual Thème : Mode Clair / Mode Sombre pour un confort visuel optimal.
    Optimisation : Recherche instantanée et pagination fluide.

:tools: Installation et Démarrage
1. Prérequis

Assurez-vous d'avoir Python installé sur votre système.
2. Installation des dépendances

pip install -r requirements.txt

3. Initialisation de la base de données

L'application est fournie avec une base SQLite pré-configurée. Pour réinitialiser ou migrer :

python manage.py migrate

4. Lancement de l'application

python manage.py runserver

Accédez à l'interface via : http://localhost:8000
:wrench: Stack Technique

    Backend : Django 5.x (Python)
    Frontend : Vanillia JS & CSS Modern (Variables CSS)
    PDF Engine : ReportLab
    Base de données : SQLite 3

© 2026 - Développé par Andéol du Chouchet pour le test ALLTOO.
