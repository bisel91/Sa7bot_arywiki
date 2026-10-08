import wikipedia
from TTS.api import TTS
from google.colab import drive
drive.mount('/content/drive')
# Load your fine-tuned model
tts = TTS(model_path="output_model/best_model.pth")
tts.finetune(
    train_csv="my_dataset/metadata.csv",
    output_path="output_model/",
    eval_split=0.1,
    num_epochs=20,      # fewer epochs
    batch_size=4,       # smaller batch
)
