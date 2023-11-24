from langchain.llms import OpenAI, HuggingFacePipeline
import os
import json
from dotenv import load_dotenv
load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"

#######################
# Step 1: Initializing the LLM Model (GPT-3)   
#######################

#callbacks=[StreamingStdOutCallbackHandler()]
print("LLM: ready")
#######################
# Step 2: Building the Knowledge Base
#######################

import pinecone
pinecone.init(  
    api_key=os.environ.get('PINECONE_API_KEY'),
    environment=os.environ.get('PINECONE_ENV')
)
index_name = 'duhocsinh-se'  
index = pinecone.Index(index_name)
print("Pinecone DB: ready")

#######################
# Step 3: Initializing the Embedding Pipeline (Hugging Face Sentence Transformer)
# Embed model                                               
# maps sentences & paragraphs to a 384-dimensional dense vector space
# and can be used for tasks like clustering or semantic search.
#######################

from langchain.embeddings.huggingface import HuggingFaceEmbeddings
embed_model_id = 'sentence-transformers/all-MiniLM-L6-v2'
device = 'cpu'
embed_model = HuggingFaceEmbeddings(
    model_name=embed_model_id,
    model_kwargs={'device': device},
    encode_kwargs={'device': device, 'batch_size': 32}
)
print("Embed model: ready")

#######################
# Step 4: Initializing the RetrievalQA Component
# Langchain to glue the components together  
#######################

from langchain.vectorstores import Pinecone
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate


text_field = 'text'  # field in metadata that contains text content                              
vectorstore = Pinecone(index,
                       embed_model,
                       text_field)

prompt_template = """Answer ONLY with the facts listed in the list of sources below. If there isn't enough information below, say you don't know. Do not generate answers that don't use the sources below. For tabular information return it as an html table. Do not return markdown format. If the question is not in English, answer in the language used in the question. For every fact in your answer, cite the source by including its URL inside square brackets. Do not include a source list.

{context}

Question: {question}
Helpful Answer:"""
QA_PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)
document_prompt = PromptTemplate(input_variables=["page_content", "source"], template="\n\nSource URL: {source}\n{page_content}")

#######################
# Result
#######################
#res = generate_text({"question": "What are the conditions for permanent residence permit in Sweden?", "chat_history": []})
#res = llm.stream("What are the conditions for permanent residence permit in Sweden?")
#res = generate_text.stream({"question": "How much does it cost to study a Master's program in Sweden?", "chat_history": []})
#for word in res:
#    continue
# {
#    'query': 'What is deep convolutional nets?',
#    'result': " I don't know.",
#    'source_documents': [
#        Document(
#            page_content='abc',
#            meta_data='{"source":"...url...","title":"abc"}'
#        )
#    ]
# }

def text_transform(res):
    source_documents = []
    for document in res['source_documents']:
        doc = document.to_json()
        if 'kwargs' in doc:
            source_documents.append(doc['kwargs']['metadata'])
    return json.dumps({
        'choices': [ {
                'index': 0,
                'message': {
                    'content': res['answer']
                },
                'context': {
                    'followup_questions': [],
                    'data_points': source_documents
                },
                'session_state': None
            }]
    })

"""     return json.dumps({
        'result': res['answer'],
        'source_documents': source_documents
    }) """

def stream_transform(res):
    return json.dumps({
        'choices': [ {
                'index': 0,
                'delta': {
                    'content': res['answer']
                },
                'context': {
                    'followup_questions': [],
                    'data_points': []
                },
                'session_state': None
            }]
    })

def build_prompt(messages):
    chat_history = []
    num_messages = len(messages)
    if num_messages % 2 == 1:
        num_char_in_chat_history = 0
        for i in reversed(range((num_messages-1)//2)):
            formatted_question = messages[2*i]['content']
            formatted_response = messages[2*i+1]['content'].split("\n\n&nbsp; \n\n**", 1)[0]
            if num_char_in_chat_history + len(formatted_question) + len(formatted_response) > 3841:
                break
            chat_history.insert(0, (formatted_question, formatted_response))
            num_char_in_chat_history += len(formatted_question) + len(formatted_response)
    #return {"question": messages[-1]['content'], "chat_history": chat_history}
    return {"question": messages[-1]['content'], "chat_history": []}

from typing import AsyncIterable, Awaitable
import asyncio
async def wrap_done(fn: Awaitable, event: asyncio.Event):
        """Wrap an awaitable with a event to signal when it's done or an exception is raised."""
        try:
            await fn
        except Exception as e:
            # TODO: handle exception
            print(f"Caught exception: {e}")
        finally:
            # Signal the aiter to stop.
            event.set()

def get_generate_text(stream_callback):
    llm = OpenAI(temperature=0, model_name='text-davinci-003',request_timeout=120,streaming=True,callbacks=[stream_callback])
    generate_text = ConversationalRetrievalChain.from_llm(llm=llm,
                                                        retriever=vectorstore.as_retriever(
                                                            search_kwargs={"k": 4},
                                                            search_type="mmr",
                                                            score_threshold=0.3),
                                                        combine_docs_chain_kwargs={
                                                            'prompt': QA_PROMPT,
                                                            'document_prompt': document_prompt
                                                        },
                                                        return_source_documents=False)
    return generate_text