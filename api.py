from flask import Flask, json, request
from flask_cors import CORS, cross_origin

#from llmodels.llamma2 import *
#from llmodels.gpt2 import *
from llmodels.gpt3 import *
#from llmodels.rag-gpt3 import *
                                      
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/q', methods=['GET','POST','OPTIONS'])
@cross_origin()
def get_companies():
    if request.method == 'POST':
        content_type = request.headers.get('Content-Type')
        if (content_type != 'application/json'):
            return content_type
        prompt = "Question: " + request.json['inputCode'] + "\n" \
                 + "Answer: "
        res = generate_text(prompt)
        response = res if isinstance(res, str) else (res['result'] if hasattr(res, 'result') else res[0]["generated_text"])
        response = response[len(prompt):]+"..." if prompt in response else response
        return response
    elif request.method == 'GET':
        return 'It is working'

#if __name__ == '__main__':
#    app.run(host='0.0.0.0',port=8000,debug=False,ssl_context=('cert.pem', 'key.pem')) #ssl_context='adhoc'
