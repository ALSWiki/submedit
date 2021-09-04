import smtplib
import ssl

class GMAIL:
    def __init__(self, email: str, password: str):
        port = 465 # ssl port

        self._email = email
        self._ctx = ssl.create_default_context()
        self._server = smtplib.SMTP_SSL("smtp.gmail.com", port, context=self._ctx)
        self._server.login(email, password)


    def send_message(self, to: str, subject: str, message: str):
        formatted_message = f"""
Subject: {subject}

{message}
"""
        self._server.sendmail(self._email, to, formatted_message)


    def __del__(self):
        self._server.close()
