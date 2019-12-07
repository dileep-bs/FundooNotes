class Respond:
    msg = MIMEMultipart()
    payload = {'id': x[0]}
    key = os.getenv('key')
    algorithm = os.getenv('algorithm')
    token = jwt.encode(payload=payload, key=key, algorithm=algorithm).decode('utf-8')
    print(token)
    message = f"http:(os.getenv('IP')/reset_token/{token}"
    print(message)
    # setup the parameters of the message
    password = os.getenv('password')
    msg['From'] = os.getenv('email')
    msg['To'] = email_id
    msg['Subject'] = "Subscription"

    # add in the message body
    msg.attach(MIMEText(message, 'plain'))

    # create server
    server = smtplib.SMTP('smtp.gmail.com: 587')

    server.starttls()

    # Login Credentials for sending the mail
    server.login(msg['From'], password)

    # send the message via the server.
    server.sendmail(msg['From'], [msg['To']], msg.as_string())

    server.quit()

new=Respond()