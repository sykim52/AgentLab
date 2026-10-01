# Training lifecycle

**Rule:** Benchmark Llama · Mistral · Qwen → **pick one** → LoRA/QLoRA → adapter → ModelRegistry → demo.

Do not fine-tune all three. Do not commit weights (`adapters/` is gitignored).

| Path | Purpose |
|------|---------|
| `configs/{llama,mistral,qwen}/` | Reproducible YAML (model_id, revision, PEFT hyperparams) |
| `evaluation/compare_models.py` | Stage-1 selection helper |
| `finetuning/train_*.py` | Planned PEFT entrypoints |
| `adapters/` | Local artifacts only |
