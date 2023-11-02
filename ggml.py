# choose your champion
#model_id = "TheBloke/Llama-2-7B-GGML"
model_id = "TheBloke/Llama-2-7B-chat-GGML"
#model_id = "TheBloke/Llama-2-13B-GGML"
#model_id = "TheBloke/Llama-2-13B-chat-GGML"

from ctransformers import AutoModelForCausalLM
import torch

config = {'max_new_tokens': 256, 'repetition_penalty': 1.1, 'temperature': 0.1, 'stream': True}

llm = AutoModelForCausalLM.from_pretrained(model_id,
                                           model_type="llama",
                                           model_file="llama-2-7b-chat.ggmlv3.q5_K_M.bin",
                                           #lib='avx2', #for cpu use
                                           gpu_layers=130, #110 for 7b, 130 for 13b
                                           **config
                                           )

"""## LLAMA-2-7B-Chat tests

### Tokenizer
"""

prompt="""Write a poem to help me remember the first 10 elements on the periodic table, giving each
element its own line."""

tokens = llm.tokenize(prompt)

tokens

"""### Pipeline"""

# 'pipeline' execution
llm(prompt, stream=False)

prompt2 = """Quando e por quem o Brasil foi descoberto?"""
llm(prompt2, stream=False)

"""### Generate with stream execution"""

# LlAMA-2-7b-chat execution
import time
start = time.time()
NUM_TOKENS=0
print('-'*4+'Start Generation'+'-'*4)
for token in llm.generate(tokens):
    print(llm.detokenize(token), end='', flush=True)
    NUM_TOKENS+=1
time_generate = time.time() - start
print('\n')
print('-'*4+'End Generation'+'-'*4)
print(f'Num of generated tokens: {NUM_TOKENS}')
print(f'Time for complete generation: {time_generate}s')
print(f'Tokens per secound: {NUM_TOKENS/time_generate}')
print(f'Time per token: {(time_generate/NUM_TOKENS)*1000}ms')

"""## LLAMA-2-13B-Chat tests

### Tokenizer
"""

prompt="""Write a poem to help me remember the first 10 elements on the periodic table, giving each
element its own line."""

tokens = llm.tokenize(prompt)

tokens

"""### Pipeline"""

# 'pipeline' execution
llm(prompt, stream=False)

prompt2 = """Quando e por quem o Brasil foi descoberto?"""
llm(prompt2, stream=False)

"""### Stream generation"""

# LlAMA-2-13b-chat execution
import time
start = time.time()
NUM_TOKENS=0
print('-'*4+'Start Generation'+'-'*4)
for token in llm.generate(tokens):
    print(llm.detokenize(token), end='', flush=True)
    NUM_TOKENS+=1
time_generate = time.time() - start
print('\n')
print('-'*4+'End Generation'+'-'*4)
print(f'Num of generated tokens: {NUM_TOKENS}')
print(f'Time for complete generation: {time_generate}s')
print(f'Tokens per secound: {NUM_TOKENS/time_generate}')
print(f'Time per token: {(time_generate/NUM_TOKENS)*1000}ms')

"""## LangChain Integration

https://python.langchain.com/docs/ecosystem/integrations/ctransformers
"""
