from flask import Flask, json

companies = [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]

api = Flask(__name__)

@api.route('/companies', methods=['GET'])
def get_companies():
    return json.dumps(companies)

if __name__ == '__main__':
    api.run(host="localhost", port=8000, debug=False)
