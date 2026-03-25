# Doframe v1.3.1

**Doframe** est un outil de gestion multi-comptes pour le jeu **Dofus**, permettant de jouer avec plusieurs personnages de manière fluide et organisée depuis un seul poste.

> Ce projet est un dump du code source de Doframe. Il ne m'appartient pas et n'est pas de mon idée. Je le publie uniquement dans un souci de transparence, afin d'éviter que des versions modifiées avec du code malveillant ne circulent. (puis les créateurs de dofus l'ont fait supprimer par son créateur original...)

---

## Fonctionnalités

### Gestion des comptes
- Ajout et organisation de plusieurs comptes Dofus
- Activation / désactivation individuelle des comptes
- Détection et affichage de la classe du personnage
- Système de groupes et de désignation de leader

### Macros et automatisations
- **Clic synchronisé** — synchronise les clics gauche/droit sur tous les personnages
- **Auto-Zaap** — téléportation automatique avec délai configurable
- **Invitation de groupe** — envoie automatiquement les invitations de groupe à tous les comptes
- **Coller + Entrée** — colle le presse-papier et valide sur tous les personnages
- **Échange de drop XP** — basculement rapide du drop d'XP entre personnages (clic sur le bouton du chall...)

### Interface
- Menu radial (menu circulaire) pour basculer rapidement entre les personnages
- Overlay flottant au-dessus du jeu avec des boutons d'action rapide
- Gestionnaire de personnages dédié
- Thème sombre par défaut
- Infobulles sur les éléments de l'interface
- Contrôle de la vitesse de clic (Lent / Normal / Rapide)

### Intégration système (Windows)
- Icône dans la barre des tâches système (systray)
- Support des dispositions clavier AZERTY et QWERTY
- Raccourcis clavier entièrement configurables
- Gestion avancée des fenêtres via l'API Win32
- Détection des conflits avec d'autres logiciels (ex. organizer.exe)

---

## Prérequis

- Windows 10 / 11
- Python 3.14 (max je n'ai pas test d'autre version)
- Les dépendances listées dans `requirements.txt`

---

## Installation

```bash
git clone https://github.com/votre-repo/doframe.git
cd doframe
pip install -r requirements.txt
python main.py
```

Vous pouvez également télécharger une archive ZIP du projet et l'extraire localement, puis suivre les mêmes étapes à partir de l'extraction. (cd ./doframe)

---

## Version éxécutables ?

Pour le moment ce n'est pas prévu mais si vraiment les utilisateurs n'y arrivent pas nous pourrions faire une version éxécutable avec pyinstaller ou autre.

---

## Contribution
- Forkez le projet et créez une branche pour votre fonctionnalité ou correction de bug
- Soumettez une pull request avec une description détaillée de vos changements
- Assurez-vous que votre code suit les conventions de style et est bien documenté

--- 

## Avertissement

Ce logiciel est destiné à un usage personnel uniquement. L'utilisation de logiciels tiers avec Dofus peut être contraire aux conditions d'utilisation d'Ankama. Utilisez-le à vos propres risques.

Ce dépôt est un dump public du code source original (Doframe v1.3.1). Aucune modification du comportement du programme n'a été apportée.
