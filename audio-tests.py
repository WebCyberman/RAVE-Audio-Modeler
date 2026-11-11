import soundfile as sf
import librosa
from pathlib import Path

for f in list(Path("dataset/violin/wav").glob("*.wav"))[:20]:
    info = sf.info(str(f))
    print(f.name)
    print(info)
    print("-"*40)

count = 0

for f in Path("dataset/violin/wav").glob("*.wav"):
    try:
        y, sr = librosa.load(str(f), sr=None, mono=True)
        count += 1
    except Exception as e:
        print(f.name, e)

print("Lisibles:", count)
