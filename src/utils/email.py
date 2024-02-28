import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
        print(e)
    finally:
        server.quit()


def send_new_reservation_email(reciever_email):
    message = MIMEMultipart("alternative")
    message["Subject"] = "TdA - Nová rezervace"
    message["From"] = sender_email
    message["To"] = reciever_email

    text = """\
    Dobrý den,
    byla Vám vytvořena nová rezervace. Můžete ji zobrazit, potvrdit nebo smazat zde.
    """
    html = """\
    <html>
    <body>
        <p>Dobrý den,<br>
        byla Vám vytvořena nová rezervace. Můžete ji zobrazit, potvrdit nebo smazat zde.<br>
        </p>
    </body>
    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    send_email(reciever_email, message)

def send_reservation_confirmed_email(reciever_email):
    message = MIMEMultipart("alternative")
    message["Subject"] = "TdA - Nová rezervace"
    message["From"] = sender_email
    message["To"] = reciever_email

    text = """\
    Dobrý den,
    byla Vám vytvořena nová rezervace. Můžete ji zobrazit, potvrdit nebo smazat zde.
    """
    html = """\
    <html>
    <body>
        <p>Dobrý den,<br>
        byla Vám vytvořena nová rezervace. Můžete ji zobrazit, potvrdit nebo smazat zde.<br>
        </p>
    </body>
    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    send_email(reciever_email, message)

def send_reservation_deleted_email(reciever_email):
    message = MIMEMultipart("alternative")
    message["Subject"] = "TdA - Nová rezervace"
    message["From"] = sender_email
    message["To"] = reciever_email

    text = """\
    Dobrý den,
    byla Vám vytvořena nová rezervace. Můžete ji zobrazit, potvrdit nebo smazat zde.
    """
    html = """\
    <html>
    <body>
        <p>Dobrý den,<br>
        byla Vám vytvořena nová rezervace. Můžete ji zobrazit, potvrdit nebo smazat zde.<br>
        </p>
    </body>
    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    send_email(reciever_email, message)