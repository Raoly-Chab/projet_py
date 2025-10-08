# Snake AI avec Tkinter (BFS + Cycle Hamiltonien)

Ce projet est une version améliorée du jeu Snake en Python utilisant **Tkinter** et une **IA hybride** :

- **BFS (Breadth First Search)** : l’IA essaie toujours de trouver le chemin le plus court vers la pomme.  
- **Cycle Hamiltonien (sécurité)** : si aucun chemin sûr n’est trouvé, l’IA suit un cycle Hamiltonien couvrant toute la grille, ce qui garantit qu’elle ne se coince jamais.  

Ainsi, le serpent est **rapide** au début et **immortel** en fin de partie. 🎮

---

## 🚀 Fonctionnalités

- Grille **600x600 pixels**, divisée en cases **20x20**.
- Serpent commence avec **3 segments**.
- Pomme générée aléatoirement (jamais sur le serpent).
- **IA automatique** :
  - BFS vers la pomme en priorité.
  - Cycle Hamiltonien comme chemin de secours.
- Option `WRAP_EDGES` :
  - `False` (défaut) : toucher un bord reste une limite.
  - `True` : activer le *wrap-around* (le serpent traverse un côté et réapparaît de l’autre).
- Score affiché en haut de la fenêtre.
- Message **GAME OVER** si collision.

---

## 🖥️ Installation et lancement

### Prérequis
- Python 
- Tkinter 

### Lancer le jeu
```bash

