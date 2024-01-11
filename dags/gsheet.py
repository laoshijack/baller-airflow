import os
import csv

from google.oauth2 import service_account
from googleapiclient import discovery


def generate_user_list():
    scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
    secret_file = os.path.join(os.getcwd(), 'client_secret.json')

    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    range_name = 'Sheet1!A1:D'

    credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=scopes)
    service = discovery.build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    result_input = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range=range_name).execute()

    values_input = result_input.get('values', [])
    print(values_input)

    with open('email_list.csv', 'w') as f:
        
        # using csv.writer method from CSV package
        write = csv.writer(f)

        write.writerows(values_input)


if __name__ == "__main__":
    generate_user_list()

    