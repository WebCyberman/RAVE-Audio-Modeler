import subprocess
import sys
import time
import yaml
import GPUtil
import soundfile as sf

from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


# ============================================================
# OUTILS
# ============================================================

def run_command(cmd):
    """
    Lance une commande et affiche la sortie en temps réel.
    """

    console.print(f"\n[cyan]>>> {' '.join(cmd)}[/cyan]\n")

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        universal_newlines=True
    )

    while True:

        line = process.stdout.readline()

        if not line and process.poll() is not None:
            break

        if line:
            print(line.rstrip())

    return process.wait()

# ============================================================
# CONVERT
# ============================================================

SUPPORTED = [
    ".wav",
    ".mp3",
    ".flac",
    ".aiff",
    ".aif",
    ".ogg",
    ".m4a"
]

def convert_to_wav(source_dir, wav_dir):
    """
    Convertit tous les fichiers audio vers WAV mono 44.1 kHz.
    """

    wav_dir.mkdir(parents=True, exist_ok=True)

    files = []

    for ext in SUPPORTED:
        files.extend(source_dir.rglob(f"*{ext}"))

    for index, src in enumerate(files, start=1):

        dst = wav_dir / f"{index:06d}.wav"

        print(
            f"[{index}/{len(files)}] "
            f"{src.name}"
        )

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(src),
                "-ar",
                "44100",
                "-ac",
                "1",
                str(dst)
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    return len(files)

# ============================================================
# DATASET
# ============================================================

def scan_dataset(dataset_path):

    wavs = list(dataset_path.rglob("*.wav"))

    if not wavs:
        raise RuntimeError("Aucun fichier WAV trouvé.")

    total_seconds = 0
    sample_rates = set()
    channels = set()

    for wav in wavs:

        info = sf.info(str(wav))

        total_seconds += info.frames / info.samplerate
        sample_rates.add(info.samplerate)
        channels.add(info.channels)

    table = Table(title="Dataset")

    table.add_column("Propriété")
    table.add_column("Valeur")

    table.add_row("Fichiers WAV", str(len(wavs)))
    table.add_row("Durée", f"{total_seconds / 60:.2f} min")
    table.add_row("Sample Rates", str(sorted(sample_rates)))
    table.add_row("Canaux", str(sorted(channels)))

    console.print(table)

    return len(wavs)


# ============================================================
# GPU
# ============================================================

def show_gpu():

    gpus = GPUtil.getGPUs()

    if not gpus:
        console.print("[red]Aucun GPU détecté[/red]")
        return None

    gpu = gpus[0]

    table = Table(title="GPU")

    table.add_column("Champ")
    table.add_column("Valeur")

    table.add_row("Nom", gpu.name)
    table.add_row("Id", str(gpu.id))
    table.add_row("VRAM", f"{gpu.memoryTotal} MB")
    table.add_row("Load", f"{gpu.load * 100:.1f}%")

    console.print(table)

    return gpu.id


# ============================================================
# PREPROCESS
# ============================================================

def preprocess(dataset_path, output_path):

    output_path.mkdir(parents=True, exist_ok=True)

    cmd = [
        "rave",
        "preprocess",
        "--input_path",
        str(dataset_path),
        "--output_path",
        str(output_path),
        "--lazy"
    ]

    code = run_command(cmd)

    if code != 0:
        raise RuntimeError("Le preprocess a échoué.")

    metadata = output_path / "metadata.yaml"

    if metadata.exists():

        with open(metadata, "r") as f:
            meta = yaml.safe_load(f)

        console.print(
            Panel.fit(
                f"Durée dataset : {meta['n_seconds']/3600:.2f} h\n"
                f"Sample Rate : {meta['sr']}\n"
                f"Channels : {meta['channels']}",
                title="Preprocess OK"
            )
        )


# ============================================================
# TRAIN
# ============================================================

def train(dataset_db, runs_path, model_name, gpu_id=0):

    cmd = [
        "rave",
        "train",
        "--name",
        model_name,
        "--db_path",
        str(dataset_db),
        "--out_path",
        str(runs_path),
        "--channels",
        "1",
        "--gpu",
        str(gpu_id)
    ]

    run_command(cmd)


# ============================================================
# MENU
# ============================================================

def main():

    console.print(
        Panel.fit(
            "RAVE Dataset Manager",
            style="bold green"
        )
    )

    source_dir = Path(
        input(
            "\nAudio Source : "
        ).strip()
    )

    dataset = Path(
        input(
            "\nDataset WAV : "
        ).strip()
    )

    convert_to_wav(source_dir, dataset)

    db = Path(
        input(
            "Dossier preprocess : "
        ).strip()
    )

    runs = Path(
        input(
            "Dossier training : "
        ).strip()
    )

    model_name = input(
        "Nom du modèle : "
    ).strip()

    scan_dataset(dataset)

    gpu = show_gpu()

    console.print(
        "\n[yellow]Préprocessing...[/yellow]"
    )

    preprocess(dataset, db)

    console.print(
        "\n[green]Entraînement...[/green]"
    )

    train(
        dataset_db=db,
        runs_path=runs,
        model_name=model_name,
        gpu_id=gpu
    )


if __name__ == "__main__":
    main()
