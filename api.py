from flask import Flask, json, request
from flask_cors import CORS, cross_origin

#from llmodels.gpt3 import *
from llmodels.rag_gpt3 import *
#from llmodels.rag_gpt4 import *
                                      
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/q', methods=['GET','POST','OPTIONS'])
@cross_origin()
def q_post():
    if request.method == 'POST':
        content_type = request.headers.get('Content-Type')
        if (content_type != 'application/json'
            or 'messages' not in request.json
            or len(request.json['messages']) == 0):
            return app.response_class(
                response="Invalid request",
                status=500
            )
        
        prompt = build_prompt(request.json['messages'])
        
        return app.response_class(
            response=text_transform(generate_text(prompt)),
            status=200,
            mimetype='application/json'
        )
        
    elif request.method == 'GET':
        return 'It is working'

def build_prompt(messages):
    prompt = "I want you to act as an information assistant who specializes in laws and information regarding studying and living in Sweden. If you don't know the answer to any question, answer that you are only knowledgeable about studying and living in Sweden. \n\n"
    for message in messages:
        prompt += message['role'].capitalize() + ": " + message['content'] + "\n"
    #return messages[-1]['content']

#if __name__ == '__main__':
#    app.run(host='0.0.0.0',port=8000,debug=False,ssl_context=('cert.pem', 'key.pem')) #ssl_context='adhoc'
