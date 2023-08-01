import win32com.client as win
import time 
import datetime
import os
from PIL import Image
import glob
import sqlite3
from shareplum import Site, Office365
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

def RefreshBalance():
    try:
        #call excel to open
        NegativeStart = win.Dispatch("Excel.Application")
        NegativeStart.Visible = True #makes excel visible
        
        #open negative balance workbook
        NegativeBalance = NegativeStart.Workbooks.open(r"A:\Daily Reports\Negative Balance\App\NegBal.xlsm")
        #Refresh just in case
        NegativeBalance.RefreshAll()
        
        #Wait for query to finish
        time.sleep(45)
        
        sheetName = "Pivot (2)"
        NegativeSheet = NegativeBalance.Sheets(sheetName)
        
        #find pivot chart in sheet
        
        pivotChartIndex = 1
        pivotChart = NegativeSheet.ChartObjects(pivotChartIndex)
        
        if pivotChart is None:
                print(f"Chart not found!")
                return
            
        #get date
        
        today_date = datetime.datetime.now().strftime("%m%d%Y")
        outputFolder = r"a:\Daily Reports\Negative Balance\Daily Pivots"
        outputFile = f"negative_balance_" + today_date + ".png"
        outputfilePath = os.path.join(outputFolder, outputFile)
        
        pivotChart.Chart.Export(outputfilePath, "PNG")
        
        NegativeBalance.Save()
        NegativeBalance.Close()
        
        NegativeStart.Quit()
        
        print(f"Your Negative Balance has been updated to your folder!")
              
    except Exception as e:
        print("Error!:",e)
    
RefreshBalance()

def read_credentials_from_database():
    conn = sqlite3.connect(r"A:\Daily Reports\Negative Balance\App\TheVault.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM passwords LIMIT 1")
    data = cursor.fetchone()
    conn.close()

    if data is None:
        raise ValueError("No credentials found in the database.")

    return data

read_credentials_from_database()

def todaysDate():
    return datetime.datetime.now().strftime("%m%d%Y")

todaysDate()

def sharepoint_upload():
    try:
        folder_pivots = r'A:\Daily Reports\Negative Balance\Daily Pivots'
        list_charts = glob.glob(os.path.join(folder_pivots, '*.png'))
        print("List of PNG files:", list_charts)

        if not list_charts:
            print("No PNG files found in the folder.")
            return

        today_date = datetime.datetime.now().strftime("%m%d%Y")

        # Filter the list to include only files with today's date in their name
        file_chart = None
        for file_path in list_charts:
            filename = os.path.basename(file_path)
            if today_date in filename:
                file_chart = file_path
                break

        if not file_chart:
            print(f"No PNG files found for today's date: {today_date}.")
            return
        
        print("File to be uploaded:", file_chart)
        # Get SharePoint credentials and links
        sharepoint_url = 'https://hctx.sharepoint.com/sites/CM1-Budget'
        daily_sp_relative_url = '/sites/CM1-Budget/Reports'
        chart_sp_relative_url = '/sites/CM1-Budget/Reports/NegativeBalance'

        # Initialize the client credentials
        username, password = read_credentials_from_database()
        user_credentials = UserCredential(username, password)

        # Create client context object
        ctx = ClientContext(sharepoint_url).with_credentials(user_credentials)

        # Get NegativeBalance folder
        daily_target_folder = ctx.web.get_folder_by_server_relative_url(daily_sp_relative_url)
        chart_target_folder = ctx.web.get_folder_by_server_relative_url(chart_sp_relative_url)

        # Open and read the newly created file
        chart_name = 'negative_balance_' + todaysDate() + '.png'

        with open(file_chart, 'rb') as content_file:
            file_content = content_file.read()
            daily_target_folder.upload_file('Negative_Today.png', file_content).execute_query()
            chart_target_folder.upload_file(chart_name, file_content).execute_query()

        print(f"File uploaded successfully!")

    except IndexError as ie:
        print(f"Oops! IndexError: {ie}")

    except Exception as e:
        print(f"Oops! {e}")

if __name__ == "__main__":
    sharepoint_upload()