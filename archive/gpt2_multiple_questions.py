from transformers import AutoTokenizer, GPT2LMHeadModel, pipeline, BitsAndBytesConfig
import torch
import sys

model_id = 'gpt2'
tokenizer = AutoTokenizer.from_pretrained(model_id)

model = GPT2LMHeadModel.from_pretrained(model_id,
                                        device_map='auto',
                                        offload_folder='archive',
                                        low_cpu_mem_usage=True)
print('Write your question, type "quit" to exit')
while True:
    q = input()
    if (q=='quit'): sys.exit()
    generate_text = pipeline(
        model=model, tokenizer=tokenizer,
        return_full_text=True,  # langchain expects the full text
        task='text-generation',
        max_new_tokens=512,  # mex number of tokens to generate in the output
        repetition_penalty=1.1  # without this output begins repeating
    )
    res = generate_text(q)
    print(res[0]["generated_text"])
