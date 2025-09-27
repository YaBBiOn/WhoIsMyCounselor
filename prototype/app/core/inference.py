import os
import numpy as np
import pandas as pd
import torch
import streamlit as st
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from app.infra.config import MAX_SEQ


@st.cache_resource(show_spinner=True)
def load_tokenizer_and_model(model_dir: str):
    tok = AutoTokenizer.from_pretrained(model_dir, use_fast=True, trust_remote_code=True)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "right"

    model = AutoModelForSequenceClassification.from_pretrained(
        model_dir,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
        torch_dtype=torch.float32,
        device_map=None,  # CPU
    )

    if getattr(model.config, "pad_token_id", None) is None:
        model.config.pad_token_id = tok.pad_token_id
    if hasattr(model.config, "use_cache"):
        model.config.use_cache = False
    if hasattr(model.config, "attn_implementation"):
        try:
            model.config.attn_implementation = "eager"
        except Exception:
            pass

    os.environ.setdefault("OMP_NUM_THREADS", "4")
    os.environ.setdefault("MKL_NUM_THREADS", "4")
    torch.set_num_threads(4)
    torch.set_num_interop_threads(2)

    model.to("cpu").eval()
    return model, tok

def predict_proba(texts, model, tok, max_len: int = MAX_SEQ, batch_size: int = 64) -> np.ndarray:
    if isinstance(texts, str):
        texts = [texts]
    device = next(model.parameters()).device
    out_chunks = []

    for i in range(0, len(texts), batch_size):
        batch = list(pd.Series(texts[i:i+batch_size]).fillna("").astype(str))
        enc = tok(
            batch,
            max_length=max_len,
            truncation=True,
            padding=True,
            return_tensors="pt"
        ).to(device)

        with torch.no_grad():
            logits = model(**enc).logits
        logits = logits - logits.max(dim=-1, keepdim=True).values  # overflow 방지
        probs = torch.softmax(logits.to(torch.float32), dim=-1).cpu().numpy()
        out_chunks.append(probs)

    return np.concatenate(out_chunks, axis=0)