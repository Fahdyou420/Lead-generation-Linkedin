import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import GMAIL_ADDRESS, GMAIL_APP_PASSWORD

class EmailSender:
    def send(self, to_email, subject, content_html_or_text):
        if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
            print("Gmail credentials not perfectly configured.")
            return False
            
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"Ooredoo Business <{GMAIL_ADDRESS}>"
            msg["To"] = to_email

            # Add Ooredoo branding (very simple HTML)
            html = f"""
            <html>
              <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="padding: 20px;">
                  <h2 style="color: #E30613;">Ooredoo Business</h2>
                  <p>{content_html_or_text.replace(chr(10), '<br>')}</p>
                </div>
              </body>
            </html>
            """
            
            part1 = MIMEText(content_html_or_text, "plain")
            part2 = MIMEText(html, "html")
            msg.attach(part1)
            msg.attach(part2)

            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, to_email, msg.as_string())
            server.quit()
            return True
        except Exception as e:
            print(f"Error sending email to {to_email}: {e}")
            return False
