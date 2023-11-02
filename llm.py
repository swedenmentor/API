import torch
import transformers

model_id = 'Maykeye/TinyLLama-v0'
#model_id = 'TheBloke/Llama-2-7B-fp16'

# set quantization configuration to load large model with less GPU memory
# this requires the `bitsandbytes` library
bnb_config = transformers.BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type='nf4',
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16
)

model = transformers.AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map='auto',
    offload_folder='offload',
    low_cpu_mem_usage=True,
    torch_dtype=torch.bfloat16
)
model.eval()

tokenizer = transformers.AutoTokenizer.from_pretrained(
    model_id
)

generate_text = transformers.pipeline(
    model=model, tokenizer=tokenizer,
    return_full_text=True,  # langchain expects the full text
    task='text-generation',
    max_new_tokens=128,  # mex number of tokens to generate in the output
    repetition_penalty=1.1  # without this output begins repeating
)

res = generate_text("Explain to me the difference between nuclear fission and fusion.")
print(res[0]["generated_text"])
