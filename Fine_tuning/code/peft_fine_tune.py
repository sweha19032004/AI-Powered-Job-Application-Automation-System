# fine_tuning.py

import os
import json
import pandas as pd
import pdfplumber
from docx import Document

from datasets import load_dataset, Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# ========== CONFIG ==========
MODEL_NAME = os.getenv("peft_model")
OUTPUT_DIR = "./finetuned_model/"
DOCUMENTS_DIR = "./fine_tuning/documents/"
DATASET_JSON_PATH = "./fine_tuning/dataset/train.json"

# ========== 1. LOAD DOCUMENTS ==========
def load_documents_from_folder(folder_path):
    documents = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith(".txt"):
            with open(file_path, 'r', encoding="utf-8") as f:
                documents.append(f.read())
        elif filename.endswith(".pdf"):
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                documents.append(text)
        elif filename.endswith(".docx"):
            doc = Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
            documents.append(text)
        elif filename.endswith(".csv"):
            df = pd.read_csv(file_path)
            text = df.to_string(index=False)
            documents.append(text)
    return documents

# ========== 2. PREPARE TRAINING DATA ==========
def prepare_training_data(documents):
    """Convert documents into instruction-output pairs."""
    data = []
    for doc in documents:
        sample = {
            "instruction": "Summarize the following document.",
            "input": doc,
            "output": f"This document discusses: {doc[:200]}..."  # For demo, output is partial content
        }
        data.append(sample)
    
    # Save to json
    os.makedirs(os.path.dirname(DATASET_JSON_PATH), exist_ok=True)
    with open(DATASET_JSON_PATH, 'w', encoding='utf-8') as f:
        for entry in data:
            f.write(json.dumps(entry) + "\n")
    print(f"Saved training dataset with {len(data)} examples at {DATASET_JSON_PATH}")

# ========== 3. LOAD DATASET ==========
def load_training_dataset():
    dataset = load_dataset('json', data_files=DATASET_JSON_PATH, split="train")
    return dataset

# ========== 4. TOKENIZE ==========
def tokenize_function(example, tokenizer):
    prompt = f"{example['instruction']}\n{example['input']}"
    labels = example['output']
    model_inputs = tokenizer(prompt, max_length=512, truncation=True)
    labels = tokenizer(labels, max_length=128, truncation=True)
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

# ========== 5. LOAD MODEL & APPLY LoRA ==========
def load_model_with_lora():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        load_in_8bit=True,  # Load model in 8-bit to save memory
        device_map="auto"
    )
    
    model = prepare_model_for_kbit_training(model)
    
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj"],  # Depends on model architecture
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    return model, tokenizer

# ========== 6. TRAINING ==========
def train_model(model, tokenizer, dataset):
    tokenized_dataset = dataset.map(lambda x: tokenize_function(x, tokenizer), batched=True)

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        evaluation_strategy="no",
        save_strategy="epoch",
        learning_rate=2e-4,
        num_train_epochs=2,
        save_total_limit=1,
        fp16=True,
        logging_dir="./logs",
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        tokenizer=tokenizer
    )

    trainer.train()
    model.save_pretrained(OUTPUT_DIR)
    print(f"Model saved at {OUTPUT_DIR}")

# ========== 7. MAIN ==========
def main():
    print("Loading documents...")
    documents = load_documents_from_folder(DOCUMENTS_DIR)
    
    print("Preparing dataset...")
    prepare_training_data(documents)

    print("Loading training dataset...")
    dataset = load_training_dataset()
    
    print("Loading model with LoRA...")
    model, tokenizer = load_model_with_lora()
    
    print("Training model...")
    train_model(model, tokenizer, dataset)

if __name__ == "__main__":
    main()
