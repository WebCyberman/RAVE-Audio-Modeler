🇫🇷 Version française : [README.fr.md](https://github.com/WebCyberman/RAVE-Audio-Modeler/blob/main/README.fr.md)

🇬🇧 English version : [README.md](https://github.com/WebCyberman/RAVE-Audio-Modeler/blob/main/README.md)

<div align="center">

# 🎵 RAVE Audio Modeler

### Train, export and manage RAVE models through a modern graphical interface

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-Enabled-orange.svg)
![RAVE](https://img.shields.io/badge/RAVE-Compatible-red.svg)
![FFmpeg](https://img.shields.io/badge/Audio-FFmpeg-lightgrey.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-informational.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A complete GUI for the RAVE ecosystem that allows musicians, sound designers, researchers and audio enthusiasts to create neural audio models without using the command line.

</div>

---

# 📸 Screenshots

> Add your screenshots here

| Dataset Management | Training |
|-------------------|----------|
| ![](docs/images/datasets.png) | ![](docs/images/training.png) |

| Preprocessing | Export |
|--------------|--------|
| ![](docs/images/preprocess.png) | ![](docs/images/export.png) |

---

# 🚀 Overview

**RAVE Audio Modeler** is a desktop application built with **PySide6** that simplifies the complete RAVE workflow.

Instead of manually running commands such as:

```bash
rave preprocess
rave train
rave export
```

the application provides an intuitive graphical interface that manages:

- Dataset discovery
- Audio conversion
- RAVE preprocessing
- Model training
- Checkpoint recovery
- Model export
- Progress monitoring
- Console logs

All from a single window.

---

# ✨ Features

## 📂 Dataset Management

Automatically scans the dataset folder structure and displays:

- Dataset name
- Total audio files
- WAV files
- Dataset duration
- Conversion status
- Preprocessing status

Example:

```text
dataset/
├── guitar/
├── violin/
├── piano/
└── voice/
```

---

## 🎧 Audio Conversion

Automatically converts audio files into WAV format using FFmpeg.

Supported formats:

- WAV
- MP3
- FLAC
- OGG
- AAC
- AIFF
- M4A

When conversion is launched, a dedicated `wav` folder is created:

```text
dataset/
└── guitar/
    ├── sample1.mp3
    ├── sample2.flac
    └── wav/
        ├── sample1.wav
        └── sample2.wav
```

Original files are preserved.

---

## 📊 Dataset Statistics

The application calculates:

- Number of source audio files
- Number of converted WAV files
- Total dataset duration
- Real-time dataset status

Helping users estimate whether a dataset is suitable for training.

---

## ⚙️ RAVE Preprocessing

Automatically runs:

```bash
rave preprocess
```

Features:

✅ Live console output

✅ Progress information

✅ Error reporting

✅ Automatic folder creation

✅ Non-blocking execution

Example:

```bash
rave preprocess \
    --input_path dataset/guitar/wav \
    --output_path data/guitar \
    --lazy
```

---

## 🧠 Model Training

Launches RAVE training directly from the GUI.

Features:

- Live log display
- Epoch monitoring
- Progress tracking
- Error reporting
- Safe process termination
- Automatic checkpoint recovery

Example:

```bash
rave train data/guitar
```

---

## 🔄 Automatic Checkpoint Recovery

If training is interrupted, the application automatically searches for the latest checkpoint.

Example:

```text
runs/
└── guitar/
    └── version_3/
        └── checkpoints/
            └── last.ckpt
```

The next training session resumes from the latest checkpoint instead of restarting from scratch.

---

## 📦 Model Export

Export trained models directly from the interface.

The application manages:

```bash
rave export
```

and generates TorchScript models:

```text
guitar.ts
```

usable in:

- RAVE VST
- Python
- Max/MSP
- Pure Data
- TorchScript projects
- Real-time audio applications

---

## 🧵 Multi-Threaded Architecture

Long-running tasks execute in dedicated QThreads.

Tasks running in background:

- Conversion
- Preprocessing
- Training
- Export

This keeps the GUI responsive during processing and training sessions that may last several hours or even days.

---

## 📋 Detailed Logging

Real-time feedback includes:

```text
Conversion: Guitar

[122/1457]
guitar_F3_forte.wav
```

The integrated console displays the complete output from:

- FFmpeg
- RAVE preprocess
- RAVE train
- RAVE export

---

# 📁 Project Structure

```text
RAVE-Audio-Modeler/

├── dataset/
│   ├── guitar/
│   ├── violin/
│   ├── piano/
│   └── voice/
│
├── data/
│
├── runs/
│
├── exports/
│
├── models/
│
└── logs/
```

---

# 🔥 Typical Workflow

## 1. Add Audio Files

Create a dataset directory:

```text
dataset/guitar
```

and copy your audio files into it.

---

## 2. Convert

Click:

```text
Convert Dataset
```

The application converts all supported files into:

```text
dataset/guitar/wav
```

---

## 3. Preprocess

Click:

```text
Preprocess Dataset
```

The corresponding RAVE dataset is generated:

```text
data/guitar
```

---

## 4. Train

Click:

```text
Train Model
```

Training starts immediately and progress is displayed in real time.

---

## 5. Export

Click:

```text
Export Model
```

A TorchScript model is generated and ready for use.

---

# 🎹 Supported Dataset Types

## Musical Instruments

- Piano
- Guitar
- Violin
- Cello
- Flute
- Saxophone
- Trumpet
- Clarinet
- Drums

## Voice

- Singing
- Speech
- Narration
- Choir
- Beatboxing

## Sound Design

- Ambient recordings
- Textures
- Sound effects
- Synthesizers
- Experimental audio

---

# 🛠 Requirements

## Software

- Python 3.10+
- FFmpeg
- PyTorch
- PyTorch Lightning
- RAVE
- PySide6

## GPU (Recommended)

For training large datasets:

- NVIDIA GPU
- CUDA-compatible PyTorch installation

CPU-only training is possible but significantly slower.

---

# 📦 Installation

Clone the repository:

```bash
git clone https://github.com/WebCyberman/RAVE-Audio-Modeler.git

cd RAVE-Audio-Modeler
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# ⚠ RAVE Dependency License

RAVE Audio Modeler is an independent graphical frontend for the RAVE ecosystem.

RAVE itself is developed by IRCAM and distributed under:

**Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**

Users remain responsible for complying with the licensing terms of RAVE and any associated models.

Official RAVE repository:

https://github.com/acids-ircam/RAVE

---

# 🙏 Credits

This project would not exist without the incredible work of the IRCAM team and the creators of RAVE.

Special thanks to:

- IRCAM
- ACIDS Team
- PyTorch Community
- FFmpeg Project
- PySide6 / Qt

---

# 🤝 Contributing

Contributions are welcome.

Possible contribution areas:

- New export options
- Linux support improvements
- Dataset visualization
- Training statistics
- Hyperparameter management
- Multi-model workflows

Feel free to open an issue or submit a pull request.

---

# ⭐ Support The Project

If you find this project useful:

- ⭐ Star the repository
- 🐛 Report bugs
- 💡 Suggest new features
- 🔀 LICENSE file for details.

---

<div align="center">

### 🎵 Train your own neural instruments with RAVE

Made with ❤️ by WebCyberman

</div>
