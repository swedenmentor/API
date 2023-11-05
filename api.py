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
def get_companies():
    if request.method == 'POST':
        content_type = request.headers.get('Content-Type')
        if (content_type != 'application/json'
            or 'messages' not in request.json
            or len(request.json['messages']) == 0):
            return app.response_class(
                response="Invalid request",
                status=500
            )
        
        prompt = request.json['messages'][-1]['content']
        
        return app.response_class(
            response=text_transform(generate_text(prompt)),
            status=200,
            mimetype='application/json'
        )
        
    elif request.method == 'GET':
        return 'It is working'

#if __name__ == '__main__':
#    app.run(host='0.0.0.0',port=8000,debug=False,ssl_context=('cert.pem', 'key.pem')) #ssl_context='adhoc'
