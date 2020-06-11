from flask import Flask
from flask_restful import Resource, Api,reqparse, abort
from flask_cors import CORS


app = Flask(__name__)
api = Api(app)
CORS(app)

parser = reqparse.RequestParser()
parser.add_argument('email')
parser.add_argument('name')
parser.add_argument('text')
parser.add_argument('subject')

class SendEmail(Resource):
    def post(self):
        return {'hello': 'world'}

class Test(Resource):
    def post(self):
        args = parser.parse_args()
        print(args)
        return {'body': args}

api.add_resource(SendEmail, '/email-contact')
api.add_resource(Test, '/')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')