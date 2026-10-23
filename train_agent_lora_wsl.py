import os
import torch
from unsloth import FastLanguageModel
from unsloth.chat_templates import get_chat_template
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset

# 1. Инициализация параметров
max_seq_length = 2048
dataset_path = './agent_dataset.jsonl'
output_dir = './qwen_actor_agent'

print("🚀 Инициализация модели Qwen 2.5 (3B) через Unsloth...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Qwen2.5-3B-Instruct",
    max_seq_length=max_seq_length,
    load_in_4bit=True,
    dtype=None,
)

# 2. Настройка Chat Template для вызова функций
tokenizer = get_chat_template(tokenizer, chat_template="qwen")

def formatting_prompts_func(examples):
    convos = examples["messages"]
    texts = [tokenizer.apply_chat_template(convo, tokenize=False, add_generation_prompt=False) for convo in convos]
    return {"text": texts}

# 3. Загрузка и форматирование датасета
print(f"📦 Загрузка датасета из {dataset_path}...")
dataset = load_dataset("json", data_files=dataset_path, split="train")
dataset = dataset.map(formatting_prompts_func, batched=True)

# 4. Настройка LoRA адаптера
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
)

# 5. Конфигурация тренера
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    dataset_num_proc=2,
    packing=False,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        max_steps=60,
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=1,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=3407,
        output_dir="outputs",
    ),
)

# 6. Запуск обучения
print("🔥 Запуск процесса fine-tuning...")
trainer_stats = trainer.train()

# 7. Экспорт в GGUF для Ollama
print("💾 Сохранение модели в формат GGUF (Q4_K_M)...")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
model.save_pretrained_gguf(output_dir, tokenizer, quantization_method="q4_k_m")
print(f"✅ Готово! Модель сохранена в {output_dir}")

