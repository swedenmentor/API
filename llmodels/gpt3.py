from langchain.llms import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

query = "How many planets are there in the solar system?"
generate_text = OpenAI(temperature=0, model_name='text-davinci-003')

def text_transform(res):
    return json.dumps({
        'result': res,
        'source_documents': []
    })

#print(text_transform(generate_text("what is the meaning of life?")))
