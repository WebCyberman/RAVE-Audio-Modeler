# Changelog

Tous les changements notables de ce projet sont documentés dans ce fichier.

---

# [1.0.0] - 2026-11-16

## 🎉 Première version stable

Cette version marque la première release complète de RAVE Audio Modeler avec une pipeline entièrement fonctionnelle permettant de passer d'un dataset audio à un modèle TorchScript exploitable.

---

## ✨ Fonctionnalités

### Gestion des datasets

- Scan automatique des datasets
- Sélection multiple de datasets
- Affichage des informations détaillées
- Comptage des fichiers audio
- Comptage des fichiers WAV
- Actualisation automatique des statuts

### Conversion audio

- Conversion automatique vers WAV
- Support des principaux formats audio
- Intégration FFmpeg
- Conversion vers 44.1 kHz mono
- Affichage du fichier en cours de traitement
- Gestion des erreurs de conversion

### Préprocess RAVE

- Intégration de `rave preprocess`
- Affichage des logs en temps réel
- Lecture automatique du fichier `metadata.yaml`
- Détection automatique de la durée du dataset
- Détection du sample rate
- Détection du nombre de canaux

### Entraînement

- Intégration de `rave train`
- Affichage des logs d'entraînement
- Affichage des epochs en temps réel
- Détection automatique des checkpoints
- Reprise automatique depuis le dernier checkpoint disponible
- Validation préalable des datasets préprocessés

### Export

- Intégration de `rave export`
- Export TorchScript streaming
- Détection automatique des runs RAVE
- Détection automatique des exports existants
- Affichage des logs d'export

### Pipeline complète

Ajout d'une pipeline automatique permettant :

```text
Audio
 ↓
WAV
 ↓
DB
 ↓
CKPT
 ↓
TS
```

La pipeline détecte automatiquement les étapes déjà réalisées et ne relance que les traitements nécessaires.

Exemples :

```text
Audio → WAV → DB → CKPT → TS
```

```text
DB → CKPT → TS
```

```text
CKPT → TS
```

```text
TS → Aucun traitement
```

### Arrêt des traitements

- Arrêt de la conversion
- Arrêt du préprocess
- Arrêt de l'entraînement
- Arrêt de l'export
- Arrêt propre de la pipeline complète

---

## ✅ Détection des états

Ajout des statuts automatiques :

| Statut | Signification |
|----------|----------|
| 🔴 Audio | Dataset brut |
| 🟠 WAV | Conversion terminée |
| 🟡 DB | Préprocess terminé |
| 🔵 CKPT | Checkpoint disponible |
| ✅ TS | Export TorchScript disponible |

---

## 🖥 Interface

- Interface PySide6 complète
- Journal des opérations en temps réel
- Barre de progression
- Informations détaillées sur chaque dataset
- Activation automatique des actions disponibles
- Mise à jour automatique après traitement

---

## 🔧 Corrections

- Correction de la détection des checkpoints RAVE
- Correction de l'activation du bouton Export
- Correction de la détection des exports TorchScript
- Correction de la gestion des threads Qt
- Correction des crashs lors de la fermeture des workers
- Amélioration de la robustesse de la pipeline
- Amélioration de la reprise des entraînements

---

## 🚀 Technologies

- Python 3.11
- PySide6
- FFmpeg
- acids-rave 2.3.1
- PyTorch
- TorchScript

---

## 🎯 Objectif atteint

Pipeline complète fonctionnelle :

```text
Dataset Audio
       ↓
   Conversion
       ↓
   Préprocess
       ↓
 Entraînement
       ↓
    Export
       ↓
 Modèle TorchScript
```

---

**Version : v1.0.0**
