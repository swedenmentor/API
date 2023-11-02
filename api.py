from flask import Flask, json, request
from flask_cors import CORS, cross_origin
from llm import *

                                      
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
        res = generate_text(request.json['inputCode'])
        response = res[0]["generated_text"]
        return response
    elif request.method == 'GET':
        return 'It is working'

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000,debug=False,ssl_context=('cert.pem', 'key.pem')) #ssl_context='adhoc'
