from langchain.llms import OpenAI
from dotenv import load_dotenv

load_dotenv()

query = "How many planets are there in the solar system?"
generate_text = OpenAI(temperature=0, model_name='text-davinci-003')
