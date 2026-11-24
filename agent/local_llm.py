
import os
from pathlib import Path

# ==========================================
# FORCE OFFLINE MODE
# ==========================================

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


# ==========================================
# LOCAL QWEN MODEL
# ==========================================

MODEL_PATH = (
    Path.home()
    / ".cache"
    / "huggingface"
    / "hub"
    / "models--Qwen--Qwen2.5-1.5B-Instruct"
    / "snapshots"
    / "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
)

tokenizer = None
model = None


# ==========================================
# LOAD LOCAL MODEL
# ==========================================

def load_model():

    global tokenizer, model

    if model is not None:
        return

    if not (MODEL_PATH / "model.safetensors").exists():

        raise FileNotFoundError(
            f"Qwen model not found at: {MODEL_PATH}"
        )

    print("Loading APEX local Qwen model...")

    tokenizer = AutoTokenizer.from_pretrained(
        str(MODEL_PATH),
        local_files_only=True
    )

    model = AutoModelForCausalLM.from_pretrained(
        str(MODEL_PATH),
        local_files_only=True,
        dtype=torch.float32,
        low_cpu_mem_usage=True
    )

    model.eval()

    print("APEX Qwen model ready!")


# ==========================================
# GENERATE ENGLISH F1 ANSWER
# ==========================================

def generate_response(question):

    if not question or not question.strip():

        return "Please ask a Formula 1 question."

    load_model()

    messages = [

        {
            "role": "system",

            "content": (
                "You are APEX, an intelligent and professional "
                "Formula 1 racing assistant. "

                "IMPORTANT LANGUAGE RULE: "
                "Always answer in clear, natural English, "
                "regardless of whether the user asks in English, "
                "Urdu, or Roman Urdu. Never answer in Urdu. "

                "Answer the user's actual question directly. "

                "Explain Formula 1 drivers, teams, circuits, "
                "rules, engines, aerodynamics, tyres, DRS, "
                "pit stops and racing strategies clearly. "

                "Use simple English when explaining technical topics. "

                "Organize longer answers with headings or bullet points "
                "when useful. "

                "Do not invent live race data, results, or statistics. "

                "If you do not know something, clearly say so. "

                "Stay focused on Formula 1 and motorsport."
            )
        },

        {
            "role": "user",
            "content": question.strip()
        }

    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=2048
    )

    with torch.inference_mode():

        outputs = model.generate(
            **inputs,
            max_new_tokens=300,
            do_sample=False,
            repetition_penalty=1.08,
            pad_token_id=tokenizer.eos_token_id
        )

    answer_tokens = outputs[
        0,
        inputs["input_ids"].shape[1]:
    ]

    answer = tokenizer.decode(
        answer_tokens,
        skip_special_tokens=True
    ).strip()

    if not answer:
        return "APEX could not generate an answer. Please try again."

    return answer
