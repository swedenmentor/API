import torch
import transformers

model_id = 'Maykeye/TinyLLama-v0'

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
    device_map='auto'
)
model.eval()


tokenizer = transformers.AutoTokenizer.from_pretrained(
    model_id
)

generate_text = transformers.pipeline(
    model=model, tokenizer=tokenizer,
    return_full_text=True,  # langchain expects the full text
    task='text-generation',
    # we pass model parameters here too
    temperature=0.0,  # 'randomness' of outputs, 0.0 is the min and 1.0 the max
    max_new_tokens=512,  # mex number of tokens to generate in the output
    repetition_penalty=1.1  # without this output begins repeating
)

res = generate_text("Explain to me the difference between nuclear fission and fusion.")
print(res[0]["generated_text"])
