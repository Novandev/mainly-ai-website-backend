from flask import Flask,request
from flask_cors import CORS,cross_origin
from celery_worker import make_celery
import yagmail
import logging
import os
from dotenv import load_dotenv


load_dotenv()
SENGRID_API = os.getenv("SENDGRID_API_KEY")
M_PASSWORD = os.getenv("M_PASSWORD")
USER_NAME = os.getenv("USER_NAME")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
app.config['CORS_HEADERS'] = "Content-Type"
app.config['CORS_RESOURCES'] = {r"/*": {"origins": "*"}}






celery = make_celery(app)

@celery.task()
def add_together(a, b):
    return a + b


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


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    print(response)
    return response

# Argument parsers for Flask-restful
@app.route("/email-contact/")
@cross_origin()
def email_contact():
    args = request.args
    send_contact_email_yagmail(args['email'],args['subject'],args['text'])
    return {'body': args}

if __name__ == '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.run(debug=True,host='0.0.0.0')