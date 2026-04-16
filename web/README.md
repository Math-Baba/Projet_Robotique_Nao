# Interface Web du Projet NAO

Cette interface web permet de piloter les modules du projet depuis un navigateur.

## Lancer l'interface

1. Installer les dépendances Python du projet (Flask et requests sont déjà listés dans `requirements_py310.txt`).
2. Depuis la racine du projet :

```bash
python web/app.py
```

3. Ouvrir ensuite :

```text
http://127.0.0.1:8000
```

## Fonctions disponibles

- Sauvegarde et test de l'adresse IP du robot NAO
- Lancement des scénarios Odysseo
- Lancement du jeu QR
- Lancement des modules de contrôle motion
- Lancement du système d'IA complet, du chatbot seul ou de la reconnaissance faciale seule
- Arrêt de tous les processus démarrés depuis l'interface

## Remarques

- Le front-end est servi par Flask depuis `web/app.py`.
- Les scripts NAO sont lancés depuis les chemins Python configurés dans `config/python_paths.py`.
