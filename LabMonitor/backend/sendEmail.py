import smtplib, ssl

port = 587  # For SSL
smtp_server = "smtp.office365.com"
sender_email = "cqtdr@nus.edu.sg"  # Enter your address
receiver_email = "416640656@qq.com"  # Enter receiver address
password = "Wangyinhan11081"
message = """\
Subject: Hi there

This message is sent from Python."""

context = ssl.create_default_context()
with smtplib.SMTP(smtp_server, port) as server:
    server.ehlo()  # Can be omitted
    server.starttls(context=context)
    server.ehlo()  # Can be omitted
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)