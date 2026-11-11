# 🎵 RAVE Audio Modeller

Interface graphique PySide6 permettant de préparer, prétraiter, entraîner et exporter facilement des modèles **RAVE (Realtime Audio Variational AutoEncoder)** pour la synthèse et la transformation sonore.

Ce projet automatise l'ensemble du workflow de création de modèles RAVE à partir de collections audio personnalisées (instruments, voix, bruitages, textures sonores, etc.) sans avoir à utiliser manuellement les commandes en ligne de commande.

---

## ✨ Fonctionnalités

### 📂 Gestion des datasets

- Détection automatique des datasets présents dans le dossier `dataset/`
- Affichage :
  - Nom du dataset
  - Nombre de fichiers audio
  - Durée totale du dataset
  - État de conversion
  - État du prétraitement
- Sélection rapide du dataset à utiliser

---

### 🎧 Conversion audio

Conversion automatique vers le format compatible RAVE :

Formats supportés :

- WAV
- MP3
- FLAC
- OGG
- AIFF
- AAC
- M4A

Lorsqu'un dataset contient des fichiers dans différents formats, l'application :

1. Analyse le contenu du dossier
2. Crée automatiquement un sous-dossier `wav`
3. Convertit les fichiers à l'aide de **FFmpeg**
4. Conserve les fichiers d'origine

Exemple :

```
dataset/
└── violin/
    ├── instrument1.mp3
    ├── instrument2.flac
    └── wav/
        ├── instrument1.wav
        └── instrument2.wav
```

---

### ⚙️ Prétraitement RAVE

L'application lance automatiquement :

```bash
rave preprocess
```

avec les paramètres appropriés.

Fonctionnalités :

- Affichage en temps réel de la sortie console
- Affichage de la progression
- Gestion des erreurs
- Création automatique des dossiers dans `data/`

Exemple :

```bash
rave preprocess \
    --input_path dataset/violin/wav \
    --output_path data/violin \
    --lazy
```

---

### 🧠 Entraînement des modèles

Lancement direct de :

```bash
rave train
```

avec suivi complet de l'entraînement.

Suivi en temps réel :

- Logs RAVE
- Epochs
- Étapes de calcul
- Messages d'erreur
- Fin d'entraînement

L'exécution est réalisée dans un thread dédié afin d'éviter le gel de l'interface graphique.

---

### 📦 Export des modèles

Export simplifié des modèles entraînés :

```bash
rave export
```

Possibilité de sélectionner :

- Fichier `.ckpt`
- Nom du modèle exporté
- Nombre de canaux

Les fichiers exportés peuvent ensuite être utilisés dans :

- VST RAVE
- Max/MSP
- Pure Data
- Python
- Applications compatibles TorchScript

---

### 🚀 Interface non bloquante

Toutes les opérations lourdes sont exécutées dans des **QThread dédiés** :

- Conversion
- Prétraitement
- Entraînement
- Export

L'interface reste réactive même lors d'entraînements de plusieurs heures.

---

### 📊 Retour d'information détaillé

Pendant les traitements :

- Affichage de la tâche courante
- Affichage du fichier en cours
- Compteur de progression
- Sortie console complète
- Journalisation des erreurs

Exemple :

```
Conversion : Violin

[125/1502]
violin_G3_forte.wav
```

---

## 🏗️ Structure du projet

```text
dataset/
├── violin/
│   ├── sample1.mp3
│   ├── sample2.flac
│   └── wav/
│       ├── sample1.wav
│       └── sample2.wav

data/
├── violin/
│   ├── metadata.yaml
│   └── ...

runs/
├── violin/
│   └── version_0/

models/
└── violin.ts
```

---

## 📋 Workflow recommandé

### 1. Ajouter un dataset

Créer un dossier :

```text
dataset/violin
```

et y copier vos fichiers audio.

---

### 2. Convertir

Cliquer sur :

```text
Convert Dataset
```

Tous les fichiers compatibles sont convertis dans :

```text
dataset/violin/wav
```

---

### 3. Prétraiter

Cliquer sur :

```text
Preprocess Dataset
```

L'application exécute :

```bash
rave preprocess
```

et génère les données nécessaires à l'entraînement.

---

### 4. Entraîner

Cliquer sur :

```text
Train Model
```

et suivre l'évolution directement dans la console intégrée.

---

### 5. Exporter

Une fois l'entraînement terminé :

```text
Export Model
```

pour produire un modèle utilisable en temps réel.

---

## 🔧 Dépendances

- Python 3.10+
- PySide6
- RAVE
- PyTorch
- PyTorch Lightning
- FFmpeg

---

## 🎯 Cas d'utilisation

### Instruments

- Violon
- Piano
- Guitare
- Saxophone
- Trompette
- Batterie

### Voix

- Chant
- Spoken Word
- Narration
- Beatbox

### Design sonore

- Ambiances
- Bruitages
- Textures
- Synthétiseurs

---

## 🙏 Remerciements

Ce projet repose sur l'excellent travail de l'équipe IRCAM ayant développé :

**RAVE — Realtime Audio Variational AutoEncoder**

Projet officiel :

https://github.com/acids-ircam/RAVE

---

## 📜 Licence

Ce projet est distribué sous la licence de votre choix.

```
