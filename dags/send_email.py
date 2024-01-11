import smtplib
import csv
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import time

today_date = datetime.today().strftime('%Y-%m-%d')



with open('email_list.csv', newline='') as file: 
    
    reader = csv.reader(file, delimiter = ',') 
      
    headings = next(reader) 
      
    Output = [] 
    for row in reader: 
        Output.append(row[:]) 



for x in Output: 
    you_email = x[1]
    player_id = x[2]
    season = x[3]
    html_file_name = f'html_files/{player_id}_{season}_{today_date}.html'

    print('Sending to: ', you_email)


    # me == my email address
    # you == recipient's email address
    me = os.getenv('AIRFLOW__SMTP__SMTP_USER')
    you = you_email


    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Ball Out with Apache Airflow"
    msg['From'] = me
    msg['To'] = you

    # Create the body of the message (a plain-text and an HTML version).

    html_file_path = open(html_file_name, "r")
    html = html_file_path.read()


    # Record the MIME types of both parts - text/plain and text/html.

    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.

    msg.attach(part2)
    # Send the message via local SMTP server.
    mail = smtplib.SMTP('smtp.gmail.com', 587)

    mail.ehlo()

    mail.starttls()

    mail.login(os.getenv('AIRFLOW__SMTP__SMTP_USER'), os.getenv('AIRFLOW__SMTP__SMTP_PASSWORD'))
    mail.sendmail(me, you, msg.as_string())
    mail.quit()
    time.sleep(5)


