
import os
import tempfile
from pathlib import Path

# Force local-only model loading
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from faster_whisper import WhisperModel


MODEL_ROOT = Path(
    "D:/HuggingFaceCache/hub/models--Systran--faster-whisper-base"
)

whisper_model = None


def load_whisper():
    global whisper_model

    if whisper_model is not None:
        return whisper_model

    snapshots = list((MODEL_ROOT / "snapshots").iterdir())

    if not snapshots:
        raise FileNotFoundError(
            "Whisper model snapshot was not found."
        )

    model_path = snapshots[0]

    print("Loading APEX offline Whisper model...")

    whisper_model = WhisperModel(
        str(model_path),
        device="cpu",
        compute_type="int8",
        cpu_threads=4,
        local_files_only=True
    )

    print("APEX Whisper ready!")

    return whisper_model


def transcribe_audio(audio_file):
    if audio_file is None:
        return "", ""

    model = load_whisper()

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as temp_audio:

            temp_audio.write(audio_file.getvalue())
            temp_path = temp_audio.name

        segments, info = model.transcribe(
            temp_path,
            language=None,
            beam_size=5,
            vad_filter=True
        )

        transcript = " ".join(
            segment.text.strip()
            for segment in segments
        ).strip()

        detected_language = info.language

        return transcript, detected_language

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
