from transformers import AutoTokenizer, GPT2LMHeadModel, pipeline, BitsAndBytesConfig
import torch

model_id = 'gpt2'
tokenizer = AutoTokenizer.from_pretrained(model_id)

model = GPT2LMHeadModel.from_pretrained(model_id,
                                        device_map='auto',
                                        offload_folder='offload',
                                        low_cpu_mem_usage=True)
q = '''Question: What is quantum mechanics?
Answer: '''

generate_text = pipeline(
    model=model, tokenizer=tokenizer,
    return_full_text=True,  # langchain expects the full text
    task='text-generation',
    max_new_tokens=512,  # mex number of tokens to generate in the output
    repetition_penalty=1.1,  # without this output begins repeating
    pad_token_id=tokenizer.eos_token_id
)
res = generate_text(q)
print(res[0]["generated_text"])
