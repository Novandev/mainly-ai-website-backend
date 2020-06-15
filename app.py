from flask import Flask
from flask_restful import Resource, Api,reqparse, abort
from flask_cors import CORS
from celery_worker import make_celery
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging
import os
app = Flask(__name__)
api = Api(app)
CORS(app)

app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)


celery = make_celery(app)

@celery.task()
def add_together(a, b):
    return a + b

@celery.task()
def send_contact_email(email,subject,text):
    message = Mail(
    from_email='d@mainlyai.com',
    to_emails=email,
    subject=subject,
    html_content=text)
    try:
        sg = SendGridAPIClient(api_key='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')
        response = sg.send(message)
        # print(response.status_code)
        # print(response.body)
        # print(response.headers)
    except Exception as e:
        logging.warning(e)


# Argument parsers for Flask-restful
parser = reqparse.RequestParser()
parser.add_argument('email')
parser.add_argument('name')
parser.add_argument('text')
parser.add_argument('subject')

class SendEmail(Resource):
    def post(self):
        args = parser.parse_args()
        send_contact_email(args['email'],args['subject'],args['text'])
        return {'body': args}


api.add_resource(SendEmail, '/email-contact/')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')