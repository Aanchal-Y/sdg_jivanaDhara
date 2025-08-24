from datasets import load_dataset
from trl import DPOTrainer
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments

model_id = "gpt2"  # swap for a small instruct model on HF
dataset = load_dataset("json", data_files="dataset.json")["train"].train_test_split(test_size=0.2)

tok = AutoTokenizer.from_pretrained(model_id)
if tok.pad_token is None:
    tok.pad_token = tok.eos_token

model = AutoModelForCausalLM.from_pretrained(model_id)

args = TrainingArguments(
    output_dir="dpo-out",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    num_train_epochs=1,
    learning_rate=1e-5,
    fp16=False,
    logging_steps=10,
    save_steps=200,
    save_total_limit=2,
    report_to="none"
)

trainer = DPOTrainer(
    model=model,
    ref_model=model,              # simple baseline; in practice use a frozen ref
    args=args,
    beta=0.1,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    tokenizer=tok,
)

trainer.train()
trainer.save_model("dpo-out")
