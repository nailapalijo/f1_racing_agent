
import os
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


# ==========================================
# APEX MODEL CONFIGURATION
# ==========================================

LOCAL_MODEL_PATH = (
    Path.home()
    / ".cache"
    / "huggingface"
    / "hub"
    / "models--Qwen--Qwen2.5-1.5B-Instruct"
    / "snapshots"
    / "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
)

LOCAL_MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"

# Smaller model for Streamlit Cloud
CLOUD_MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"

tokenizer = None
model = None


# ==========================================
# LOAD MODEL
# ==========================================

def load_model():

    global tokenizer, model

    if model is not None:
        return

    if (LOCAL_MODEL_PATH / "model.safetensors").exists():

        model_source = str(LOCAL_MODEL_PATH)
        local_mode = True

        print("Loading APEX local Qwen 1.5B...")

    else:

        model_source = CLOUD_MODEL_ID
        local_mode = False

        print("Loading APEX Cloud Qwen 0.5B...")

    tokenizer = AutoTokenizer.from_pretrained(
        model_source,
        local_files_only=local_mode
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_source,
        local_files_only=local_mode,
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True
    )

    model.eval()

    print("APEX AI model ready!")


# ==========================================
# GENERATE ENGLISH F1 ANSWER
# ==========================================

def generate_response(question):

    if not question or not question.strip():
        return "Please ask a Formula 1 question."

    try:

        load_model()

        messages = [
            {
                "role": "system",
                "content": (
                    "You are APEX, a professional Formula 1 assistant. "
                    "Always answer in clear, natural English, even when "
                    "the user asks in Urdu or Roman Urdu. "
                    "Answer the actual question directly. "
                    "Explain F1 drivers, teams, circuits, rules, engines, "
                    "aerodynamics, tyres, DRS, pit stops and strategies. "
                    "Use simple English. Never invent live race data "
                    "or statistics. If unsure, say so. "
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
            max_length=1024
        )

        with torch.inference_mode():

            outputs = model.generate(
                **inputs,
                max_new_tokens=200,
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

    except Exception as e:

        print("APEX AI ERROR:", str(e))

        return f"APEX AI engine error: {str(e)}"
