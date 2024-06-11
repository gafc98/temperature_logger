import os
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path
import sys
import pandas as pd
from re import fullmatch
from dotenv import load_dotenv # pip install python-dotenv
from print_logs import logs_to_list
import matplotlib.pyplot as plt
import matplotlib.dates
import datetime
from tabulate import tabulate

# constants
PORT = 587
EMAIL_SERVER = "smtp.gmail.com"
DATE_FORMAT = "%a %b %d %H:%M:%S %Y"

# load .env variables
curr_dir = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
envars = curr_dir / ".env"
load_dotenv(envars)

# Read environment variables
sender_email = os.getenv("SENDER_EMAIL")
receiver_email = os.getenv("RECEIVER_EMAIL")
sender_password = os.getenv("PASSWORD")
sheet_id = os.getenv("SHEET_ID")
unsubscribe_link = os.getenv("UNSUBSCRIBE_LINK")

# function and class definitions
def is_valid_email(email):
    # Check if the email is a valid format
    regex = r'[^@]+@[^@]+\.[^@]+'
    return True if fullmatch(regex, email) else False

def average(lst): 
    return sum(lst) / len(lst) 

class EmailSender:
    def __init__(self):
        self.data_frame = None
        self.keys = None
        self.valid_emails = None

    def set_data_frame(self, sheet_id):
        self.data_frame = pd.read_csv(f"https://docs.google.com/spreadsheets/d/e/{sheet_id}/pub?output=csv")
        print(self.data_frame)
        self.keys = self.data_frame.keys()

    def set_valid_emails(self):
        self.valid_emails = set()
        invalid_emails = set()
        for email, subscribe_option in zip(reversed(self.data_frame[self.keys[1]]), reversed(self.data_frame[self.keys[2]])):
            subscribe_option = subscribe_option.lower()
            email = email.lower()
            if is_valid_email(email) and subscribe_option == "subscribe" and email not in invalid_emails:
                self.valid_emails.add(email)
            else:
                invalid_emails.add(email)

    
    def send_emails(self, date, message):
        msg = MIMEMultipart('alternative')

        msg["Subject"] = f"Eindhoven Weather Report - Week {date.strftime('%V')} of {date.strftime('%Y')}"
        msg["From"] = formataddr(("Weekly Reports", f"{sender_email}"))
        #msg["To"] = ""
        #msg["BCC"] = ", ".join(list(self.valid_emails))

        with open('weather_report.png', 'rb') as f:
            img_data = f.read()

        msg.attach(MIMEText(message, 'html'))
        image = MIMEImage(img_data, name=os.path.basename("weather_report.png"))

        #part = MIMEText('<img src="cid:image1">', 'html')
        #msg.attach(part)

        image.add_header('Content-ID', '<image1>')
        msg.attach(image)

        #msg.attach(part)

        with smtplib.SMTP(EMAIL_SERVER, PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())

class DataProcessor:
    def set_data(self,to_date):
        to_date = datetime.datetime.strptime(to_date, DATE_FORMAT).replace(hour=0, minute=0, second=0)
        self.days = [to_date + datetime.timedelta(days=i-7) for i in range(8)]
        self.days_data = []
        for i in range(len(self.days) - 1):
            print(self.days[i].strftime(DATE_FORMAT))
        
            logs_list = logs_to_list(self.days[i], self.days[i + 1])
            time_stamp_list = []
            T_list = []
            H_list = []
            P_list = []
            Tint_list = []
            for log in logs_list:
                time_stamp, T, H, P, Tint, _ = log.split('\t')
                time_stamp_list.append(datetime.datetime.strptime(time_stamp, DATE_FORMAT))
                T_list.append(float(T))
                H_list.append(float(H))
                P_list.append(float(P))
                Tint_list.append(float(Tint))
            self.days_data.append((time_stamp_list, T_list, H_list, P_list, Tint_list))

    def produce_weather_report(self):
        fig, ax = plt.subplots(len(self.days_data), 3, figsize=(25, 40))
        fig.suptitle(f'Weather report of week {self.days[0].strftime("%V")} of {self.days[0].strftime("%Y")}', fontsize=30)

        for i in range(len(self.days_data)):
            date = self.days[i].strftime("%a, %d-%m-%Y")
            time_stamp_list, T_list, H_list, P_list, Tint_list = self.days_data[i]

            ax[i, 0].plot(time_stamp_list, T_list)
            ax[i, 0].xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
            ax[i, 0].set_xlabel(date)
            ax[i, 0].set_ylabel("T [°C]")
            ax[i, 0].title.set_text('Temperature (digital sens.)')
            ax[i, 0].grid(which='both',axis='both')

            ax[i, 1].plot(time_stamp_list, H_list)
            ax[i, 1].xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
            ax[i, 1].set_xlabel(date)
            ax[i, 1].set_ylabel("H [%]")
            ax[i, 1].title.set_text('Relative Humidity')
            ax[i, 1].grid(which='both',axis='both')

            ax[i, 2].plot(time_stamp_list, P_list)
            ax[i, 2].xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
            ax[i, 2].set_xlabel(date)
            ax[i, 2].set_ylabel("P [bar]")
            ax[i, 2].title.set_text('Atmospheric Pressure')
            ax[i, 2].grid(which='both',axis='both')

            #ax[i, 3].plot(time_stamp_list, Tint_list)
            #ax[i, 3].xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
            #ax[i, 3].set_xlabel(date)
            #ax[i, 3].set_ylabel("T [°C]")
            #ax[i, 3].title.set_text('Temperature (analog sens.)')
            #ax[i, 3].grid(which='both',axis='both')

        fig.savefig('weather_report.png', dpi=fig.get_dpi()*0.6, bbox_inches = 'tight')

    def produce_email_message(self):
        # produce table data
        table_data = [{"T [°C]": round(average(day_data[1]), 2), "H [%]": round(average(day_data[2]), 1), "P [bar]": round(average(day_data[2]), 3)} for day_data in self.days_data]
        # Custom serial numbers
        table_days = [day.strftime("%a, %d-%m-%Y") for day in self.days[0:-1]]
        table = tabulate(table_data, headers="keys", showindex=table_days, tablefmt="html")

        return f"""
        <p>Dear receiver,</p>
        <p><br></p>
        <p>Hereby the weather report from my apartment in Eindhoven of <strong>week {self.days[0].strftime("%V")} of {self.days[0].strftime("%Y")}</strong>.</p>
        <p>Here's a table with the average data on each day:</p>
	    {table}
        <p><br></p>
        <p>See you next week!</p>
        <p><span style="font-size: 10px;">Don&apos;t want to receive these emails anymore? you can unsubscribe <a href="{UNSUBSCRIBE_LINK}" target="_blank" rel="noopener noreferrer">here</a>.</span></p>
<img src="cid:image1">
        """

def get_logs(from_date):
    logs_list = logs_to_list(from_date)
    print(logs_list)

if __name__ == '__main__':
    es = EmailSender()
    es.set_data_frame(sheet_id)
    es.set_valid_emails()
    
    dp = DataProcessor()
    now = datetime.datetime.now()
    from_date = (now - datetime.timedelta(days=1)).strftime(DATE_FORMAT)
    dp.set_data(from_date)
    
    dp.produce_weather_report()
    es.send_emails(dp.days[0], dp.produce_email_message())

    #es.send_emails()


