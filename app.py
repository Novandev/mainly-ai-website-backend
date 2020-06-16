from flask import Flask
from flask_restful import Resource, Api,reqparse, abort
from flask_cors import CORS
from celery_worker import make_celery
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import yagmail
import logging
import os
from dotenv import load_dotenv


load_dotenv()
SENGRID_API = os.getenv("SENDGRID_API_KEY")
M_PASSWORD = os.getenv("M_PASSWORD")
USER_NAME = os.getenv("USER_NAME")

app = Flask(__name__)
api = Api(app)
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
CORS(app, origins="*", allow_headers=[
    "Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
    supports_credentials=True)




celery = make_celery(app)

@celery.task()
def add_together(a, b):
    return a + b

@celery.task()
def send_contact_email_sendgrid(email,subject,text):
    message = Mail(
    from_email='d@mainlyai.com',
    to_emails=email,
    subject=subject,
    html_content=text)
    try:
        sg = SendGridAPIClient(api_key=SENGRID_API)
        response = sg.send(message)
        # print(response.status_code)
        # print(response.body)
        # print(response.headers)
    except Exception as e:
        logging.warning(e)



@celery.task()
def send_contact_email_yagmail(email,subject,text):
    try:
        #initializing the server connection
        yag = yagmail.SMTP(user=USER_NAME, password='Dad8e3cc!@')
        #sending the email
        yag.send(to=email, subject=subject, contents=text)
    except Exception as e:
        print(e)
        logging.error(e)
        return e


# Argument parsers for Flask-restful
parser = reqparse.RequestParser()
parser.add_argument('email')
parser.add_argument('name')
parser.add_argument('text')
parser.add_argument('subject')

class SendEmail(Resource):
    @cross_origin()
    def post(self):
        args = parser.parse_args()
        send_contact_email_yagmail(args['email'],args['subject'],args['text'])
        return {'body': args}


api.add_resource(SendEmail, '/email-contact/','/email-contact')

if __name__ == '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.run(debug=True,host='0.0.0.0')