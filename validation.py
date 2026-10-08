import os
import pandas as pd

data = pd.read_csv("my_dataset/metadata.csv", sep="|", header=None, names=["file", "text"])
missing = [f for f in data["file"] if not os.path.exists(f"my_dataset/wavs/{f}.wav")]

if missing:
    print("❌ Missing audio files:", missing)
else:
    print("✅ All audio files found!")
