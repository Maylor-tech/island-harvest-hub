import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
import streamlit as st


class EmailService:
    def __init__(self, config_path="email_config.json"):
        self.config = self.load_config(config_path)

    def load_config(self, path):
        if not os.path.exists(path):
            st.error(f"Email config file not found: {path}")
            return None
        with open(path, "r") as f:
            return json.load(f)

    def send_email(self, subject, body, to_email=None):
        if not self.config or not self.config.get("enable_notifications"):
            return False, "Notifications disabled."

        smtp_server = self.config["smtp_server"]
        smtp_port = self.config["smtp_port"]
        sender = self.config["sender_email"]
        password = self.config["sender_password"]
        use_ssl = self.config.get("use_ssl", True)
        use_tls = self.config.get("use_tls", False)

        if not to_email:
            to_email = self.config.get("default_recipient")

        # Construct email
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            if use_ssl:
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context)

            else:
                server = smtplib.SMTP(smtp_server, smtp_port)
                if use_tls:
                    server.starttls()

            server.login(sender, password)
            server.sendmail(sender, to_email, msg.as_string())
            server.quit()

            return True, "Email sent successfully."

        except Exception as e:
            if self.config.get("debug", False):
                error_log = f"EMAIL_ERROR: {str(e)}\n"
                with open("database_reports/email_debug.log", "a") as f:
                    f.write(error_log)
            return False, f"Email failed: {str(e)}"


    def send_test_email(self):
        return self.send_email(
            subject="Island Harvest Engine — SMTP Test",
            body="This is a test email from the Bornfidis Island Harvest Engine."
        )
