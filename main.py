
import sys

import re
import shutil
import subprocess
import soundfile as sf
import yaml

from pathlib import Path

from PySide6.QtCore import (
    QThread,
    QObject,
    Signal,
    Slot,
    Qt,
)

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QSplitter,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QTreeWidget,
    QTreeWidgetItem,
    QTextEdit,
    QProgressBar,
    QGroupBox,
    QFormLayout,
    QHeaderView,
)

import main

SUPPORTED_AUDIO = {
    ".wav",
    ".mp3",
    ".flac",
    ".ogg",
    ".m4a",
    ".aiff",
    ".aif"
}

class ConvertWorker(QObject):

    started = Signal()
    finished = Signal()

    progress = Signal(int)

    log = Signal(str)

    task = Signal(str)

    file = Signal(str)

    def __init__(self, datasets):

        super().__init__()

        self.datasets = datasets
        self.stop_requested = False

    def stop(self):

        self.stop_requested = True

    def run(self):

        self.started.emit()

        total_datasets = len(self.datasets)

        if total_datasets == 0:

            self.log.emit(
                "Aucun dataset sélectionné."
            )

            self.finished.emit()
            return

        for dataset_index, dataset in enumerate(
            self.datasets,
            start=1
        ):

            if self.stop_requested:
                break

            self.task.emit(
                f"[{dataset_index}/{total_datasets}] "
                f"Conversion : {dataset.name}"
            )

            self.log.emit(
                f"Conversion du dataset '{dataset.name}'"
            )

            wav_dir = dataset / "wav"

            wav_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            files = []

            for entry in dataset.iterdir():

                if (
                    entry.is_file()
                    and entry.suffix.lower()
                    in SUPPORTED_AUDIO
                ):
                    files.append(entry)

            total_files = len(files)

            if total_files == 0:

                self.log.emit(
                    f"Aucun fichier audio trouvé dans "
                    f"{dataset.name}"
                )

                continue

            errors = 0

            for file_index, src in enumerate(
                files,
                start=1
            ):

                if self.stop_requested:

                    self.log.emit(
                        "Conversion interrompue."
                    )

                    break

                self.file.emit(
                    f"[{file_index}/{total_files}] "
                    f"{src.name}"
                )

                dst = (
                    wav_dir
                    / f"{file_index:06d}.wav"
                )

                try:

                    if src.suffix.lower() == ".wav":

                        shutil.copy2(
                            src,
                            dst
                        )

                    else:

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
                            stderr=subprocess.DEVNULL,
                            check=True
                        )

                except Exception as e:

                    errors += 1

                    self.log.emit(
                        f"Erreur : "
                        f"{src.name} -> {e}"
                    )

                    continue

                dataset_progress = (
                    (dataset_index - 1)
                    + (
                        file_index
                        / total_files
                    )
                )

                percent = int(
                    dataset_progress
                    / total_datasets
                    * 100
                )

                self.progress.emit(
                    percent
                )

            self.log.emit(
                f"Dataset terminé : "
                f"{dataset.name}"
            )

            self.log.emit(
                f"Erreurs : {errors}"
            )

        if self.stop_requested:

            self.task.emit(
                "Conversion interrompue"
            )

            self.file.emit("")

        else:

            self.task.emit(
                "Conversion terminée"
            )

            self.file.emit(
                "Terminé"
            )

            self.progress.emit(
                100
            )

        self.finished.emit()

class PreprocessWorker(QObject):

    started = Signal()
    finished = Signal()

    log = Signal(str)

    task = Signal(str)
    file = Signal(str)

    def __init__(self, datasets):

        super().__init__()

        self.process = None
        self.datasets = datasets
        self.stop_requested = False

    def stop(self):

        self.stop_requested = True

        if self.process:

            try:

                self.process.terminate()

            except Exception:
                pass

    def run(self):

        self.started.emit()

        total = len(self.datasets)

        if total == 0:

            self.finished.emit()
            return

        for dataset_index, dataset in enumerate(
            self.datasets,
            start=1
        ):

            if self.stop_requested:
                break

            self.task.emit(
                f"[{dataset_index}/{total}] "
                f"Préprocess : {dataset.name}"
            )

            self.log.emit("")
            self.log.emit(
                "=" * 60
            )
            self.log.emit(
                f"Préprocess du dataset "
                f"'{dataset.name}'"
            )
            self.log.emit(
                "=" * 60
            )

            wav_dir = dataset / "wav"

            if not wav_dir.exists():

                self.log.emit(
                    f"Dossier WAV absent : "
                    f"{wav_dir}"
                )

                continue

            output_dir = (
                Path("data")
                / dataset.name
            )

            output_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            try:

                self.process = subprocess.Popen(
                    [
                        get_rave_executable(),
                        "preprocess",
                        "--input_path",
                        str(wav_dir),
                        "--output_path",
                        str(output_dir)
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    universal_newlines=True,
                    bufsize=1
                )

                while True:

                    if self.stop_requested:

                        self.process.terminate()

                        self.log.emit(
                            "Préprocess interrompu."
                        )

                        break

                    line = self.process.stdout.readline()

                    if (
                        not line
                        and self.process.poll() is not None
                    ):
                        break

                    if line:

                        clean_line = line.rstrip()

                        clean_line = re.sub(
                            r"\x1b\[[0-9;]*m",
                            "",
                            clean_line
                        )

                        self.log.emit(
                            clean_line
                        )

                        self.file.emit(
                            clean_line
                        )

                return_code = self.process.wait()

                if return_code != 0:

                    self.log.emit(
                        f"Erreur preprocess "
                        f"({return_code})"
                    )

                    continue

                metadata_file = (
                    output_dir
                    / "metadata.yaml"
                )

                if metadata_file.exists():

                    try:

                        with open(
                            metadata_file,
                            "r",
                            encoding="utf-8"
                        ) as f:

                            meta = yaml.safe_load(
                                f
                            )

                        duration = (
                            meta.get(
                                "n_seconds",
                                0
                            )
                            / 3600
                        )

                        sr = meta.get(
                            "sr",
                            "?"
                        )

                        channels = meta.get(
                            "channels",
                            "?"
                        )

                        self.file.emit(
                            f"{duration:.2f} h | "
                            f"{sr} Hz | "
                            f"{channels} canal(x)"
                        )

                        self.log.emit("")
                        self.log.emit(
                            "Résultat du préprocess"
                        )

                        self.log.emit(
                            f"Durée   : "
                            f"{duration:.2f} h"
                        )

                        self.log.emit(
                            f"SR       : "
                            f"{sr}"
                        )

                        self.log.emit(
                            f"Canaux   : "
                            f"{channels}"
                        )

                    except Exception as e:

                        self.log.emit(
                            f"Erreur lecture "
                            f"metadata : {e}"
                        )

                self.log.emit(
                    f"Préprocess terminé : "
                    f"{dataset.name}"
                )

            except Exception as e:

                self.log.emit(
                    f"Erreur "
                    f"{dataset.name} : {e}"
                )

        self.file.emit(
            ""
        )

        self.task.emit(
            "Préprocess terminé"
        )

        self.process = None

        self.finished.emit()

class TrainWorker(QObject):

    started = Signal()
    finished = Signal()

    progress = Signal(int)

    log = Signal(str)

    task = Signal(str)
    file = Signal(str)

    def __init__(self, datasets):

        super().__init__()

        self.process = None
        self.datasets = datasets
        self.stop_requested = False

    def stop(self):

        self.stop_requested = True

        if self.process:

            try:
                self.process.terminate()
            except Exception:
                pass

    def run(self):

        self.started.emit()

        total = len(self.datasets)

        if total == 0:

            self.finished.emit()
            return

        for dataset_index, dataset in enumerate(
            self.datasets,
            start=1
        ):

            if self.stop_requested:
                break

            db_path = (
                Path("data")
                / dataset.name
            )

            checkpoint = get_latest_checkpoint(
                dataset.name
            )

            metadata_file = (
                    db_path
                    / "metadata.yaml"
            )

            if not metadata_file.exists():
                self.log.emit(
                    f"{dataset.name} ignoré : "
                    f"préprocess absent"
                )

                continue

            self.task.emit(
                f"[{dataset_index}/{total}] "
                f"Train : {dataset.name}"
            )

            self.log.emit("")
            self.log.emit("=" * 60)
            self.log.emit(
                f"Entraînement de "
                f"{dataset.name}"
            )
            self.log.emit("=" * 60)

            command = [
                        get_rave_executable(),
                        "train",
                        "--name",
                        dataset.name,
                        "--db_path",
                        str(db_path),
                        "--out_path",
                        "runs",
                        "--channels",
                        "1",
                        "--batch",
                        "8",
                        "--gpu",
                        "0",
                        "--save_every",
                        "50000",
                        "--val_every",
                        "10000"
                    ]

            if checkpoint:

                self.log.emit(
                    f"Reprise depuis : "
                    f"{checkpoint.name}"
                )

                command.extend(
                    [
                        "--ckpt",
                        str(checkpoint)
                    ]
                )

            else:

                self.log.emit(
                    "Aucun checkpoint trouvé."
                )

            try:

                self.process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    bufsize=1
                )

                while True:

                    if self.stop_requested:

                        self.process.terminate()

                        self.log.emit(
                            "Entraînement interrompu."
                        )

                        break

                    line = (
                        self.process.stdout.readline()
                    )

                    if (
                        not line
                        and self.process.poll()
                        is not None
                    ):
                        break

                    if line:

                        clean_line = (
                            line.rstrip()
                        )

                        clean_line = re.sub(
                            r"\x1b\[[0-9;]*[A-Za-z]",
                            "",
                            clean_line
                        )

                        match = re.search(
                            r"(\d+)%\|",
                            clean_line
                        )

                        if match:
                            self.progress.emit(
                                int(match.group(1))
                            )

                        is_epoch_line = (
                                "Epoch " in clean_line
                        )

                        is_progress_bar = (
                                "%" in clean_line
                                and "|" in clean_line
                        )

                        if not is_epoch_line and not is_progress_bar:
                            self.log.emit(
                                clean_line
                            )

                        epoch_match = re.search(
                            r"Epoch\s+(\d+)",
                            clean_line
                        )

                        if epoch_match:
                            epoch = epoch_match.group(1)

                            self.file.emit(
                                f"Epoch {epoch}"
                            )

                return_code = (
                    self.process.wait()
                )

                if return_code != 0:

                    self.log.emit(
                        f"Erreur train "
                        f"({return_code})"
                    )

                    continue

                self.log.emit(
                    f"Entraînement terminé : "
                    f"{dataset.name}"
                )

            except Exception as e:

                self.log.emit(
                    f"Erreur "
                    f"{dataset.name} : {e}"
                )

        self.file.emit("")

        self.task.emit(
            "Entraînement terminé"
        )

        self.process = None

        self.finished.emit()

class ExportWorker(QObject):

    started = Signal()
    finished = Signal()

    log = Signal(str)

    task = Signal(str)
    file = Signal(str)

    def __init__(self, datasets):

        super().__init__()

        self.process = None
        self.datasets = datasets
        self.stop_requested = False

    def stop(self):

        self.stop_requested = True

        if self.process:

            try:
                self.process.terminate()
            except Exception:
                pass

    def run(self):

        self.started.emit()

        total = len(
            self.datasets
        )

        for index, dataset in enumerate(
            self.datasets,
            start=1
        ):

            if self.stop_requested:
                break

            run_dir = get_latest_run(
                dataset.name
            )

            if run_dir is None:

                self.log.emit(
                    f"Aucun run trouvé pour "
                    f"{dataset.name}"
                )

                continue

            exports_dir = Path(
                "exports"
            )

            exports_dir.mkdir(
                exist_ok=True
            )

            output_file = (
                exports_dir
                / f"{dataset.name}.ts"
            )

            self.task.emit(
                f"[{index}/{total}] "
                f"Export : {dataset.name}"
            )

            self.log.emit(
                f"Export de {dataset.name}"
            )

            self.log.emit(
                f"Run : {run_dir.name}"
            )

            try:

                command = [
                    get_rave_executable(),
                    "export",
                    "--run",
                    str(run_dir),
                    "--output",
                    str(output_file),
                    "--name",
                    dataset.name,
                    "--streaming"
                ]

                self.process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    bufsize=1
                )

                while True:

                    if self.stop_requested:

                        self.process.terminate()

                        self.log.emit(
                            "Export interrompu."
                        )

                        break

                    line = (
                        self.process.stdout.readline()
                    )

                    if (
                        not line
                        and self.process.poll()
                        is not None
                    ):
                        break

                    if line:

                        clean_line = (
                            line.rstrip()
                        )

                        self.log.emit(
                            clean_line
                        )

                        self.file.emit(
                            clean_line
                        )

                return_code = (
                    self.process.wait()
                )

                if return_code != 0:

                    self.log.emit(
                        f"Erreur export "
                        f"({return_code})"
                    )

                    continue

                if output_file.exists():

                    self.log.emit(
                        f"Export terminé : "
                        f"{output_file.name}"
                    )

                else:

                    self.log.emit(
                        "Export terminé mais "
                        "fichier absent."
                    )

            except Exception as e:

                self.log.emit(
                    f"Erreur export : {e}"
                )

        self.process = None

        self.file.emit("")

        self.task.emit(
            "Export terminé"
        )

        self.finished.emit()

class DatasetTree(QTreeWidget):

    def __init__(self):
        super().__init__()

        self.setColumnCount(5)

        self.setHeaderLabels(
            [
                "Dataset",
                "Etat",
                "Durée",
                "Audio",
                "WAV"
            ]
        )

        self.header().setSectionResizeMode(
            0,
            QHeaderView.Stretch
        )

        self.header().setSectionResizeMode(
            1,
            QHeaderView.ResizeToContents
        )

        self.header().setSectionResizeMode(
            2,
            QHeaderView.ResizeToContents
        )

        self.header().setSectionResizeMode(
            3,
            QHeaderView.ResizeToContents
        )

        self.header().setSectionResizeMode(
            4,
            QHeaderView.ResizeToContents
        )

def check_dependencies():

    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    except FileNotFoundError:

        raise RuntimeError(
            "FFmpeg introuvable."
        )

    rave_exe = (
            Path(sys.executable).parent
            / "rave.exe"
    )

    if not rave_exe.exists():
        raise RuntimeError(
            f"RAVE introuvable : {rave_exe}"
        )

def get_rave_executable():

    return str(
        Path(sys.executable).parent
        / "rave.exe"
    )

def count_audio_files(dataset):

    count = 0

    for file in dataset.iterdir():

        if not file.is_file():
            continue

        if (
            file.suffix.lower()
            in SUPPORTED_AUDIO
        ):
            count += 1

    return count

def count_wav_files(dataset):

    wav_dir = dataset / "wav"

    if not wav_dir.exists():
        return 0

    return len(
        list(
            wav_dir.glob("*.wav")
        )
    )

def get_dataset_duration(dataset):

    metadata_file = (
        Path("data")
        / dataset.name
        / "metadata.yaml"
    )

    if metadata_file.exists():

        try:

            with open(
                metadata_file,
                "r",
                encoding="utf-8"
            ) as f:

                meta = yaml.safe_load(f)

            hours = (
                meta.get(
                    "n_seconds",
                    0
                )
                / 3600
            )

            return f"{hours:.2f} h"

        except Exception:

            pass

    wav_dir = dataset / "wav"

    if wav_dir.exists():

        try:

            seconds = 0

            for wav in wav_dir.glob("*.wav"):

                info = sf.info(
                    str(wav)
                )

                seconds += (
                    info.frames
                    / info.samplerate
                )

            return (
                f"{seconds / 3600:.2f} h"
            )

        except Exception:

            pass

    return "-"

def has_checkpoint(dataset_name):

    runs_dir = Path("runs")

    if not runs_dir.exists():
        return False

    for run_dir in runs_dir.iterdir():

        if not run_dir.is_dir():
            continue

        if not run_dir.name.startswith(
            dataset_name + "_"
        ):
            continue

        checkpoints = list(
            run_dir.rglob("*.ckpt")
        )

        if checkpoints:
            return True

    return False

def get_latest_checkpoint(dataset_name):

    runs_dir = Path("runs")

    if not runs_dir.exists():
        return None

    checkpoints = []

    for run in runs_dir.iterdir():

        if not run.is_dir():
            continue

        if not run.name.startswith(
            dataset_name + "_"
        ):
            continue

        checkpoints.extend(
            run.rglob("*.ckpt")
        )

    if not checkpoints:
        return None

    checkpoints.sort(
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    return checkpoints[0]

def get_latest_run(dataset_name):

    runs_dir = Path("runs")

    if not runs_dir.exists():
        return None

    runs = []

    for run_dir in runs_dir.iterdir():

        if not run_dir.is_dir():
            continue

        if not run_dir.name.startswith(
            dataset_name + "_"
        ):
            continue

        ckpts = list(
            run_dir.rglob("*.ckpt")
        )

        if ckpts:
            runs.append(run_dir)

    if not runs:
        return None

    runs.sort(
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    return runs[0]


# ---------------------------------------------------------
# MainWindow
# ---------------------------------------------------------

class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.dataset_root = None

        self.setWindowTitle(
            "RAVE Studio"
        )

        self.resize(
            1200,
            700
        )

        main.check_dependencies()

        self.build_ui()

    # ---------------------------------------------------------
    # INTERFACE
    # ---------------------------------------------------------

    def build_ui(self):

        central = QWidget()

        self.setCentralWidget(
            central
        )

        root_layout = QVBoxLayout(
            central
        )

        # --------------------------------------------------
        # BARRE OUTILS
        # --------------------------------------------------

        top = QHBoxLayout()

        self.lbl_dataset_root = QLabel(
            "Aucun dossier dataset"
        )

        self.btn_select = QPushButton(
            "Choisir Dataset"
        )

        self.btn_scan = QPushButton(
            "Scanner"
        )

        top.addWidget(
            self.lbl_dataset_root
        )

        top.addStretch()

        self.lbl_selection = QLabel(
            "0 dataset(s)"
        )

        top.addWidget(
            self.btn_select
        )

        top.addWidget(
            self.btn_scan
        )

        top.addWidget(
            self.lbl_selection
        )

        root_layout.addLayout(
            top
        )

        # --------------------------------------------------
        # SPLITTER
        # --------------------------------------------------

        splitter = QSplitter()

        splitter.setSizes(
            [500, 600]
        )

        root_layout.addWidget(
            splitter
        )

        # --------------------------------------------------
        # GAUCHE
        # --------------------------------------------------

        self.tree = DatasetTree()

        splitter.addWidget(
            self.tree
        )

        # --------------------------------------------------
        # DROITE
        # --------------------------------------------------

        right = QWidget()

        splitter.addWidget(
            right
        )

        right_layout = QVBoxLayout(
            right
        )

        # ----------------------------------------------
        # INFOS DATASET
        # ----------------------------------------------

        infos = QGroupBox(
            "Informations"
        )

        infos.setMaximumHeight(
            180
        )

        form = QFormLayout(
            infos
        )

        self.lbl_name = QLabel("-")
        self.lbl_path = QLabel("-")
        self.lbl_audio = QLabel("-")
        self.lbl_wav = QLabel("-")
        self.lbl_db = QLabel("-")
        self.lbl_ckpt = QLabel("-")
        self.lbl_ts = QLabel("-")

        form.addRow(
            "Nom",
            self.lbl_name
        )

        form.addRow(
            "Chemin",
            self.lbl_path
        )

        form.addRow(
            "Audio",
            self.lbl_audio
        )

        form.addRow(
            "WAV",
            self.lbl_wav
        )

        form.addRow(
            "Préprocess",
            self.lbl_db
        )

        form.addRow(
            "Checkpoint",
            self.lbl_ckpt
        )

        form.addRow(
            "Export TS",
            self.lbl_ts
        )

        right_layout.addWidget(
            infos
        )

        # ----------------------------------------------
        # ACTIONS
        # ----------------------------------------------

        actions = QGroupBox(
            "Actions"
        )

        actions.setMaximumHeight(
            230
        )

        actions_layout = QVBoxLayout(
            actions
        )

        self.btn_convert = QPushButton(
            "Convertir"
        )

        self.btn_preprocess = QPushButton(
            "Préprocess"
        )

        self.btn_train = QPushButton(
            "Entraîner"
        )

        self.btn_export = QPushButton(
            "Exporter"
        )

        self.btn_pipeline = QPushButton(
            "Pipeline Complète"
        )

        actions_layout.addWidget(
            self.btn_convert
        )

        actions_layout.addWidget(
            self.btn_preprocess
        )

        actions_layout.addWidget(
            self.btn_train
        )

        actions_layout.addWidget(
            self.btn_export
        )

        actions_layout.addWidget(
            self.btn_pipeline
        )

        right_layout.addWidget(
            actions
        )

        # ----------------------------------------------
        # PROGRESSION
        # ----------------------------------------------

        self.lbl_task = QLabel("-")
        self.lbl_file = QLabel("-")

        right_layout.addWidget(
            self.lbl_task
        )

        right_layout.addWidget(
            self.lbl_file
        )

        self.progress = QProgressBar()

        right_layout.addWidget(
            self.progress
        )

        # ----------------------------------------------
        # LOG
        # ----------------------------------------------

        self.log = QTextEdit()

        self.log.setMaximumHeight(
            200
        )

        self.log.setReadOnly(
            True
        )

        right_layout.addWidget(
            self.log
        )

        # --------------------------------------------------
        # EVENTS
        # --------------------------------------------------

        self.btn_select.clicked.connect(
            self.select_dataset_root
        )

        self.btn_scan.clicked.connect(
            self.scan_datasets
        )

        self.tree.itemSelectionChanged.connect(
            self.show_dataset_info
        )

        self.tree.itemChanged.connect(
            self.update_selection_count
        )

        self.btn_convert.clicked.connect(
            self.convert_selected
        )

        self.btn_preprocess.clicked.connect(
            self.preprocess_selected
        )

        self.btn_train.clicked.connect(
            self.train_selected
        )

        self.btn_export.clicked.connect(
            self.export_selected
        )

        self.btn_stop = QPushButton(
            "Arrêter"
        )

        self.btn_stop.setEnabled(False)

        actions_layout.addWidget(
            self.btn_stop
        )

        self.btn_stop.clicked.connect(
            self.stop_current_task
        )

    # ---------------------------------------------------------
    # CHOIX REPERTOIRE
    # ---------------------------------------------------------

    def select_dataset_root(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Dataset Root"
        )

        if not folder:
            return

        self.dataset_root = Path(folder)

        self.lbl_dataset_root.setText(
            str(folder)
        )

    # ---------------------------------------------------------
    # SCAN
    # ---------------------------------------------------------

    def scan_datasets(self):

        self.tree.clear()

        if self.dataset_root is None:
            self.write_log(
                "Aucun dossier dataset sélectionné."
            )

            return

        root = self.dataset_root

        if not root.exists():
            self.write_log(
                "Le dossier dataset n'existe plus."
            )

            return

        dataset_count = 0

        for family in sorted(root.iterdir()):

            if not family.is_dir():
                continue

            family_item = QTreeWidgetItem(
                [
                    family.name,
                    "",
                    "",
                    "",
                    ""
                ]
            )

            self.tree.addTopLevelItem(
                family_item
            )

            for dataset in sorted(family.iterdir()):

                if not dataset.is_dir():
                    continue

                if dataset.name.lower() == "wav":
                    continue

                status = self.compute_status(
                    dataset
                )

                duration = get_dataset_duration(
                    dataset
                )

                audio_count = count_audio_files(
                    dataset
                )

                wav_count = count_wav_files(
                    dataset
                )

                item = QTreeWidgetItem(
                    [
                        dataset.name,
                        status,
                        duration,
                        str(audio_count),
                        str(wav_count)
                    ]
                )

                item.setData(
                    0,
                    Qt.UserRole,
                    str(dataset)
                )

                item.setCheckState(
                    0,
                    Qt.Unchecked
                )

                family_item.addChild(
                    item
                )

                dataset_count += 1

            family_item.setExpanded(
                True
            )

        self.write_log(
            f"Scan terminé : "
            f"{dataset_count} dataset(s)"
        )

    def get_selected_datasets(self):

        datasets = []

        root = self.tree.invisibleRootItem()

        for i in range(root.childCount()):

            family = root.child(i)

            for j in range(family.childCount()):

                item = family.child(j)

                if item.checkState(0) == Qt.Checked:

                    path = item.data(
                        0,
                        Qt.UserRole
                    )

                    if path:
                        datasets.append(
                            Path(path)
                        )

        return datasets

    # ---------------------------------------------------------
    # ETAT
    # ---------------------------------------------------------

    def compute_status(self, dataset):

        wav_folder = dataset / "wav"

        data_folder = (
            Path("data")
            / dataset.name
        )

        ts_file = (
            Path("exports")
            / f"{dataset.name}.ts"
        )

        if ts_file.exists():
            return "✅ TS"

        if has_checkpoint(
                dataset.name
        ):
            return "🔵 CKPT"

        if data_folder.exists():
            return "🟡 DB"

        if wav_folder.exists():
            return "🟠 WAV"

        return "🔴 Audio"

    # ---------------------------------------------------------
    # CONVERSION
    # ---------------------------------------------------------

    def convert_selected(self):

        datasets = self.get_selected_datasets()

        if not datasets:
            self.write_log(
                "Aucun dataset sélectionné."
            )

            return

        self.progress.setRange(
            0,
            100
        )

        self.progress.setValue(0)

        self.thread = QThread()

        self.worker = ConvertWorker(
            datasets
        )

        self.worker.moveToThread(
            self.thread
        )

        self.thread.started.connect(
            self.worker.run
        )

        self.worker.started.connect(
            self.conversion_started
        )

        self.worker.finished.connect(
            self.conversion_finished
        )

        self.worker.progress.connect(
            self.progress.setValue
        )

        self.worker.task.connect(
            self.lbl_task.setText
        )

        self.worker.file.connect(
            self.lbl_file.setText
        )

        self.worker.log.connect(
            self.write_log
        )

        self.worker.finished.connect(
            self.thread.quit
        )

        self.worker.finished.connect(
            self.worker.deleteLater
        )

        self.worker.finished.connect(
            self.task_finished
        )

        self.thread.finished.connect(
            self.thread.deleteLater
        )

        self.thread.finished.connect(
            self.scan_datasets
        )

        self.thread.start()

        self.btn_convert.setEnabled(False)
        self.btn_preprocess.setEnabled(False)
        self.btn_train.setEnabled(False)
        self.btn_export.setEnabled(False)

        self.btn_stop.setEnabled(True)

    def convert_dataset(self, dataset):

        import shutil
        import subprocess

        SUPPORTED_AUDIO = {
            ".wav",
            ".mp3",
            ".flac",
            ".ogg",
            ".m4a",
            ".aiff",
            ".aif"
        }

        wav_dir = dataset / "wav"

        wav_dir.mkdir(exist_ok=True)

        files = []

        for file in dataset.iterdir():

            if (
                    file.is_file()
                    and file.suffix.lower() in SUPPORTED_AUDIO
            ):
                files.append(file)

        total = len(files)

        if total == 0:
            self.write_log(
                f"Aucun fichier audio dans {dataset.name}"
            )
            return

        # Dataset en cours
        self.lbl_task.setText(
            f"Conversion : {dataset.name}"
        )

        for index, src in enumerate(files, start=1):

            # Fichier en cours
            self.lbl_file.setText(
                f"[{index}/{total}] {src.name}"
            )

            QApplication.processEvents()

            percent = int(
                index * 100 / total
            )

            self.progress.setValue(
                percent
            )

            dst = (
                    wav_dir
                    / f"{index:06d}.wav"
            )

            if src.suffix.lower() == ".wav":

                shutil.copy2(
                    src,
                    dst
                )

            else:

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
                    ]
                )

        self.lbl_file.setText(
            "Terminé"
        )

        self.progress.setValue(
            100
        )

    # ---------------------------------------------------------
    # DETAILS
    # ---------------------------------------------------------

    def show_dataset_info(self):

        items = self.tree.selectedItems()

        if not items:
            return

        item = items[0]

        path = item.data(
            0,
            Qt.UserRole
        )

        if not path:
            return

        dataset = Path(path)

        self.lbl_name.setText(
            dataset.name
        )

        self.lbl_path.setText(
            str(dataset)
        )

        self.lbl_audio.setText(
            "Oui"
        )

        self.lbl_wav.setText(
            "Oui" if (
                dataset / "wav"
            ).exists()
            else "Non"
        )

        self.lbl_db.setText(
            "Oui" if (
                Path("data")
                / dataset.name
            ).exists()
            else "Non"
        )

        self.lbl_ckpt.setText(
            "Oui"
            if has_checkpoint(
                dataset.name
            )
            else "Non"
        )

        self.lbl_ts.setText(
            "Oui" if (
                Path("exports")
                / f"{dataset.name}.ts"
            ).exists()
            else "Non"
        )

        has_wav = (
                dataset / "wav"
        ).exists()

        self.btn_preprocess.setEnabled(
            has_wav
        )

        has_db = (
                Path("data")
                / dataset.name
        ).exists()

        self.btn_train.setEnabled(
            has_db
        )

        has_ckpt = (
                Path("runs")
                / dataset.name
        ).exists()

        self.btn_export.setEnabled(
            has_ckpt
        )

    # ---------------------------------------------------------
    # CONVERSION
    # ---------------------------------------------------------

    def conversion_started(self):

        self.progress.setRange(
            0,
            100
        )

        self.progress.setValue(0)

        self.write_log(
            "Conversion démarrée"
        )

    def conversion_finished(self):

        self.progress.setValue(
            100
        )

        self.write_log(
            "Conversion terminée"
        )

    # ---------------------------------------------------------
    # PREPROCESS
    # ---------------------------------------------------------

    def preprocess_selected(self):

        datasets = self.get_selected_datasets()

        if not datasets:
            self.write_log(
                "Aucun dataset sélectionné."
            )

            return

        self.thread = QThread()

        self.worker = PreprocessWorker(
            datasets
        )

        self.worker.moveToThread(
            self.thread
        )

        self.thread.started.connect(
            self.worker.run
        )

        self.worker.started.connect(
            self.preprocess_started
        )

        self.worker.finished.connect(
            self.preprocess_finished
        )

        self.worker.task.connect(
            self.lbl_task.setText
        )

        self.worker.file.connect(
            self.lbl_file.setText
        )

        self.worker.log.connect(
            self.write_log
        )

        self.worker.finished.connect(
            self.thread.quit
        )

        self.worker.finished.connect(
            self.worker.deleteLater
        )

        self.worker.finished.connect(
            self.task_finished
        )

        self.thread.finished.connect(
            self.thread.deleteLater
        )

        self.thread.finished.connect(
            self.scan_datasets
        )

        self.thread.start()

        self.btn_convert.setEnabled(False)
        self.btn_preprocess.setEnabled(False)
        self.btn_train.setEnabled(False)
        self.btn_export.setEnabled(False)

        self.btn_stop.setEnabled(True)

    def preprocess_started(self):

        self.progress.setRange(
            0,
            0
        )

        self.lbl_file.setText(
            "Initialisation..."
        )

        self.write_log(
            "Préprocess démarré"
        )

    def preprocess_finished(self):

        self.progress.setRange(
            0,
            100
        )

        self.progress.setValue(
            100
        )

        self.lbl_file.setText(
            "Terminé"
        )

        self.write_log(
            "Préprocess terminé"
        )

    # ---------------------------------------------------------
    # TRAIN
    # ---------------------------------------------------------

    def train_selected(self):

        datasets = self.get_selected_datasets()

        if not datasets:
            self.write_log(
                "Aucun dataset sélectionné."
            )

            return

        self.thread = QThread()

        self.worker = TrainWorker(
            datasets
        )

        self.worker.moveToThread(
            self.thread
        )

        self.thread.started.connect(
            self.worker.run
        )

        self.worker.started.connect(
            self.train_started
        )

        self.worker.finished.connect(
            self.train_finished
        )

        self.worker.task.connect(
            self.lbl_task.setText
        )

        self.worker.file.connect(
            self.lbl_file.setText
        )

        self.worker.log.connect(
            self.write_log
        )

        self.worker.progress.connect(
            self.progress.setValue
        )

        self.worker.finished.connect(
            self.thread.quit
        )

        self.worker.finished.connect(
            self.worker.deleteLater
        )

        self.worker.finished.connect(
            self.task_finished
        )

        self.thread.finished.connect(
            self.thread.deleteLater
        )

        self.thread.finished.connect(
            self.scan_datasets
        )

        self.thread.start()

        self.btn_convert.setEnabled(False)
        self.btn_preprocess.setEnabled(False)
        self.btn_train.setEnabled(False)
        self.btn_export.setEnabled(False)

        self.btn_stop.setEnabled(True)

    def train_started(self):

        self.progress.setRange(
            0,
            100
        )

        self.progress.setValue(
            0
        )

        self.write_log(
            "Entraînement démarré"
        )

    def train_finished(self):

        self.progress.setRange(
            0,
            100
        )

        self.progress.setValue(
            100
        )

        self.lbl_file.setText(
            "Terminé"
        )

        self.write_log(
            "Entraînement terminé"
        )

        self.scan_datasets()

    # ---------------------------------------------------------
    # EXPORT
    # ---------------------------------------------------------

    def export_selected(self):

        datasets = self.get_selected_datasets()

        for dataset in datasets:
            self.write_log(
                f"Export : {dataset.name}"
            )

    def export_started(self):

        self.progress.setRange(
            0,
            0
        )

        self.write_log(
            "Export démarré"
        )

    def export_finished(self):

        self.progress.setRange(
            0,
            100
        )

        self.progress.setValue(
            100
        )

        self.write_log(
            "Export terminé"
        )

        self.scan_datasets()

    def update_selection_count(self):

        if not hasattr(self, "lbl_selection"):
            return

        count = len(
            self.get_selected_datasets()
        )

        self.lbl_selection.setText(
            f"{count} dataset(s)"
        )

    def has_valid_wav_dataset(self, dataset):

        audio_count = count_audio_files(dataset)

        wav_count = len(
            list((dataset / "wav").glob("*.wav"))
        )

        return wav_count >= audio_count

    def closeEvent(self, event):

        if (
                hasattr(self, "worker")
                and self.worker is not None
        ):

            try:
                self.worker.stop()
            except Exception:
                pass

        if (
                hasattr(self, "thread")
                and isinstance(self.thread, QThread)
        ):

            try:

                self.thread.quit()

                self.thread.wait(
                    3000
                )

            except Exception as e:

                print(
                    f"Erreur fermeture thread : {e}"
                )

        event.accept()

    def stop_current_task(self):

        if (
                hasattr(self, "worker")
                and self.worker
        ):
            self.write_log(
                "Arrêt demandé..."
            )

            self.worker.stop()

    def task_finished(self):

        self.worker = None
        self.thread = None

        self.write_log(
            "Traitement terminé."
        )

        self.btn_convert.setEnabled(True)
        self.btn_preprocess.setEnabled(True)
        self.btn_train.setEnabled(True)
        self.btn_export.setEnabled(True)

        self.btn_stop.setEnabled(False)

    def write_log(self, text):

        self.log.append(text)
        self.log.ensureCursorVisible()

        scrollbar = self.log.verticalScrollBar()

        scrollbar.setValue(
            scrollbar.maximum()
        )

if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    window = MainWindow()

    window.show()

    sys.exit(
        app.exec()
    )
