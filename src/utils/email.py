import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.other import format_datetime
from main import log_error

port = os.environ.get("EMAIL_PORT", 0)
sender_email = os.environ.get("EMAIL_ADDRESS", "")
smtp_server = os.environ.get("EMAIL_SERVER", "")
password = ""


context = ssl._create_unverified_context()


def update_password():
    global password
    try:
        with open("email_password.txt", "r") as file:
            password = file.read()
    except FileNotFoundError:
        return


def send_email(reciever_mail: str, message: MIMEText):
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)

        server.sendmail(sender_email, reciever_mail, message.as_string())

    except Exception as e:
        log_error(f"Error while sending email: {e}")
    finally:
        server.quit()


def send_new_reservation_email(reciever_email, data):
    message = MIMEMultipart("alternative")
    message["Subject"] = "TdA - Nová rezervace"
    message["From"] = sender_email
    message["To"] = reciever_email

    text = f"""\
    Byla Vám vytvořena nová rezervace:

    Student: {data["student"]["first_name"]} {data["student"]["last_name"]}
    Email studenta: {data["student"]["email"]}
    Datum a čas lekce: {format_datetime(data["start_date"])} - {format_datetime(data["end_date"])}
    Dodatečné informace od studenta: {data["info"]}

    """

    part1 = MIMEText(text, "plain")

    message.attach(part1)

    send_email(reciever_email, message)

def send_reservation_confirmed_email(reciever_email, data):
    message = MIMEMultipart("alternative")
    message["Subject"] = "TdA - Rezervace potvrzena"
    message["From"] = sender_email
    message["To"] = reciever_email

    text = f"""\
    Vaše rezervace s lektorem {data["lecturer"]["first_name"]}{" " if data["lecturer"]["middle_name"] == None or "" else data["lecturer"]["middle_name"]} {data["lecturer"]["last_name"]} byla potvrzena.

    Datum a čas lekce: {format_datetime(data["start_date"])} - {format_datetime(data["end_date"])}

    """

    part1 = MIMEText(text, "plain")

    message.attach(part1)

    send_email(reciever_email, message)

def send_reservation_deleted_email(reciever_email, data):
    message = MIMEMultipart("alternative")
    message["Subject"] = "TdA - Zrušení rezervace"
    message["From"] = sender_email
    message["To"] = reciever_email

    text = f"""\
    Vaše rezervace byla zrušena lektorem, pro více informací můžete kontaktovat lektora zde {data["lecturer"]["contact"]["emails"][0]}:

    Datum a čas zrušené lekce: {format_datetime(data["start_date"])} - {format_datetime(data["end_date"])}

    """

    part1 = MIMEText(text, "plain")

    message.attach(part1)

    send_email(reciever_email, message)