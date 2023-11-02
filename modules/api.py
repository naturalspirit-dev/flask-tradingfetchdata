# Import Libraries 
from app import app
from flask import jsonify

import datetime
from sec_api import InsiderTradingApi
import pandas as pd
import shutil
import math
import time
import yfinance as yf
import http.client
import json
import os
from dotenv import load_dotenv
load_dotenv()

# Define route "/api".
@app.route('/api/', methods=['GET'])
def api():
  # return in JSON format. (For API)
  return jsonify({"message":"Hello from Flask!"})
            
# List of ticker symbols you want to fetch information for
ticker_symbols = ["AAPL", "MSFT", "GOOGL", "NONE"]  # Add more ticker symbols as needed
tickers = ['AAPL', '$AAVE'] # Add more ticker symbols as needed
dates = []

@app.route('/api/store_all/', methods=['GET'])
def store_all_insider_data():
    global ticker_symbols, dates
    insiderTradingApi = InsiderTradingApi(os.getenv('SEC_KEY'))
    all_transactions=[]
    ticker_symbols = []
    dates=[]

    try:
        excel_file_path = os.getenv('EXCEL_FILE_PATH') + '/all.xlsx'
        # Check if the Excel file already exists
        if os.path.exists(excel_file_path):
            temp_file_path = os.getenv('EXCEL_FILE_PATH') + '/temp.xlsx'
            shutil.copy(excel_file_path, temp_file_path)

            # Load the existing Excel file
            excel_reader = pd.ExcelFile(temp_file_path)

            # # Create an Excel writer to update the existing file
            excel_writer = pd.ExcelWriter(excel_file_path, engine='openpyxl')

             # Copy existing sheets to the new writer
            for sheet_name in excel_reader.sheet_names:
                df = excel_reader.parse(sheet_name)
                df.to_excel(excel_writer, sheet_name=sheet_name, index=False)

        else:
            # Create a new Excel writer if the file doesn't exist
            excel_writer = pd.ExcelWriter(excel_file_path, engine='xlsxwriter')

        for ticker in tickers:
            i=-1
            ticker_transactions=[]

            while True:
                try:
                    print(i)
                    i=i+1
                    insider_trades = insiderTradingApi.get_data({
                        "query": {"query_string": {"query": f"issuer.tradingSymbol:{ticker} AND ownerSignatureNameDate:[2020-01-01 TO 2023-09-30]"}},
                        "from": i * 50,
                        "size": "50",
                        "sort": [{ "filedAt": { "order": "desc" } }]
                    })

                    transactions = flatten_filings(insider_trades["transactions"])
                    print(f"total: => {insider_trades['total']}, {len(insider_trades['transactions'])}, {len(transactions)}, {ticker}")
                    if(insider_trades['total']['value'] == 0 or transactions == []):
                        break
                    if transactions == []:
                        continue
                    ticker_transactions.extend(transactions)

                    # # Create a separate CSV file for each 'i' value
                    # csv_file_path = os.getenv('CSV_FILE_PATH') + '/all.csv'
                    # df.to_excel(csv_file_path, mode='w' if i == 0 else 'a', header=i == 0, index=False)

                    # if all_transactions[len(all_transactions)-1]['transactionDate'] < "2020-01-01":
                    # if transactions[-1]['transactionDate'] < "2020-01-01" or transactions[-1]['periodOfReport'] < "2020-01-01":
                    #     break
                    
                    # print(all_transactions[len(all_transactions)-1]['transactionDate'], i, all_transactions[len(all_transactions)-1]['issuerTicker'])
                    print(transactions[-1]['transactionDate'], i, transactions[-1]['issuerTicker'])
                    print(len(ticker_symbols), len(transactions))

                except Exception as e:
                    print(f"error in api.py line 73 => {e}")
                    print(f"total: => {insider_trades['total']['value']}, {insider_trades['total']['relation']}")

            df = pd.DataFrame(ticker_transactions)
            if not df.empty:
                ticker.replace("/", "_").replace(":", "^")
                # Check if the sheet already exists
                if ticker in excel_writer.sheets:
                    # Update the existing sheet
                    df.to_excel(excel_writer, sheet_name=ticker, index=False, startrow=0)
                else:
                    # Create a new sheet
                    df.to_excel(excel_writer, sheet_name=ticker, index=False)

                all_transactions.extend(ticker_transactions)
        # Save and close the Excel file
        excel_writer.close()
        df = pd.DataFrame(all_transactions)
        print(insider_trades['total'])
    
    except Exception as e:
        print(f"error in api.py line 99 => {e}")
        # Save and close the Excel file
        if excel_writer:
            excel_writer.close()
        df = pd.DataFrame(all_transactions)
        print(insider_trades['total'])

    (pd.DataFrame(ticker_symbols)).to_csv(os.getenv('CSV_FILE_PATH')+'/ticker_symbols.csv')
    (pd.DataFrame(dates)).to_csv(os.getenv('CSV_FILE_PATH')+'/dates.csv')
    return df.to_html()

@app.route('/api/tickers/', methods=['GET'])
def ticker_table():
    # Create an empty list to store ticker information
    ticker_info_list = []

    print(len(ticker_symbols))
    # Iterate through the ticker symbols and fetch information for each one
    for symbol in ticker_symbols:
        try:
            print(symbol)
            # Create a Ticker object for the current symbol
            ticker = yf.Ticker(symbol)

            # Fetch ticker information
            ticker_info = ticker.info

            # Append the ticker information to the list
            ticker_info_list.append(ticker_info)
        except Exception as e:
            print(f"error in api.py line 95 => {e}")


    # Display the fetched ticker information for all symbols
    rows=[]
    for ticker_info in ticker_info_list:
        row = {
            'Symbol': ticker_info.get('symbol', 'N/A'),
            'Company Name': ticker_info.get('longName', 'N/A'),
            'Industry': ticker_info.get('industry', 'N/A'),
            'Analyst Forecast': f"{ticker_info.get('targetMeanPrice', 'N/A')} USD"
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    # Return the JSON data as a response
    df.to_csv(os.getenv('CSV_FILE_PATH')+ '/tickers.csv', index=False)
    return df.to_html()

@app.route('/api/time_series/', methods=['GET'])
def time_series():
    conn = http.client.HTTPSConnection("api.finazon.io")
    headers = { 'Authorization': f"apikey {os.getenv('FINAZON_KEY')}" }
    # Get the current time
    current_time = datetime.datetime.now()

    html=''
    excel_file_path = os.getenv('EXCEL_FILE_PATH') + '/time_series.xlsx'
    # Create an Excel writer
    excel_writer = pd.ExcelWriter(excel_file_path, engine='xlsxwriter')

    try:
        for index, ticker_symbol in enumerate(ticker_symbols):
            try:
                date_object = datetime.datetime.utcfromtimestamp(dates[index])
                # Format the date as a string
                formatted_date = date_object.strftime('%Y-%m-%d %H:%M:%S')
                print(formatted_date, index)

                # Define the given date
                given_date = datetime.datetime.strptime(formatted_date, '%Y-%m-%d %H:%M:%S')

                # Calculate the difference in days
                days_difference = (current_time - given_date).days
                base_url = f"/latest/time_series?publisher=sip&ticker={ticker_symbol}&interval=1d&order=desc&start_at={dates[index]}"
                MAX_PAGE_SIZE = 1000
                all_datas = []

                # Handle pagination
                for page in range((days_difference + MAX_PAGE_SIZE - 1) // MAX_PAGE_SIZE):
                    offset = page * MAX_PAGE_SIZE
                    limit = min(MAX_PAGE_SIZE, days_difference - offset)
                    
                    conn.request("GET", f"{base_url}&page={page+1}&page_size={MAX_PAGE_SIZE}", headers=headers)
                    res = conn.getresponse()
                    data = res.read()
                    # Parse the JSON string
                    data_dict = json.loads(data.decode("utf-8"))

                    # Extract the "data" field
                    if 'data' not in data_dict:
                        continue
                    
                    print("limit => ", limit)

                    datas = data_dict["data"]
                    print(len(datas))
                    all_datas.extend(datas)
                    print(len(all_datas))

                    if(len(datas) < MAX_PAGE_SIZE):
                        break

                all_datas = all_datas[:days_difference]

                for item in all_datas:
                    # Convert to a datetime object
                    date_object = datetime.datetime.utcfromtimestamp(item['t'])
                    # Format the date as a string
                    formatted_date = date_object.strftime('%Y-%m-%d %H:%M:%S')
                    item['t'] = formatted_date

                if datas == []:
                    continue

                df = pd.DataFrame(all_datas)
                html += f'<h3>{ticker_symbol}</h3>'
                html += df.to_html()

                # Write the data to a new sheet in the Excel file
                sheet_name = f'{ticker_symbol}'
                df.to_excel(excel_writer, sheet_name=sheet_name, index=False)

                time.sleep(6)
            except Exception as e:
                print(f"error in api.py line 219 => {e}")
                continue

        # Save and close the Excel file
        excel_writer.close()
    except Exception as e:
        print(f"error in api.py line 221 => {e}")
        excel_writer.close()

    return html

@app.route('/api/stocks/', methods=['GET'])
def stocks():
    conn = http.client.HTTPSConnection("api.finazon.io")
    headers = { 'Authorization': f"apikey {os.getenv('FINAZON_KEY')}" }
    global tickers
    
    tickers=[]
    i=-1
    while True:
        i=i+1
        conn.request("GET", f"/latest/tickers/stocks?page={i}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        # Parse the JSON string
        data_dict = json.loads(data.decode("utf-8"))
        # Extract the "data" field
        datas = data_dict["data"]
        if(datas == []):
            break

        # Iterate through the data and add unique tickers to the set
        for item in datas:
            if item["ticker"] not in tickers:
                tickers.append(item["ticker"])

    df = pd.DataFrame(tickers)
    df.to_csv(os.getenv('CSV_FILE_PATH')+'/stocks.csv', index=False)
    return df.to_html()

# Now 'data' contains the list of dictionaries under the "data" key
def flatten_filing(filing):
  transactions = []

  # data points to be added to each transaction
  base_data = {"periodOfReport": filing["periodOfReport"], 
               "issuerCik": filing["issuer"]["cik"],
               "issuerTicker": filing["issuer"]["tradingSymbol"],
               "reportingPerson": filing["reportingOwner"]["name"]
               }
  
  if 'nonDerivativeTable' not in filing:
    print(f"warning in api.py line 201 => filing")
    return []

  # ignore filing in case no non-derivative transactions was reported
  if "transactions" not in filing["nonDerivativeTable"]:
    print(f"warning in api.py line 206 => filing['nonDerivativeTable']")
    return []
  # extract the data points of interest from each transaction
  for transaction in filing["nonDerivativeTable"]["transactions"]:
    try:
        entry = {
            "transactionDate": transaction["transactionDate"],
            "securityTitle": transaction["securityTitle"],
            "codingCode": transaction["coding"]["code"],
            "acquiredDisposed": transaction["amounts"]["acquiredDisposedCode"],
            "shares": transaction["amounts"]["shares"],
            "sharePrice": transaction["amounts"]["pricePerShare"],
            "total": math.ceil(transaction["amounts"]["shares"] * transaction["amounts"]["pricePerShare"]),
            "sharesOwnedFollowingTransaction": transaction["postTransactionAmounts"]["sharesOwnedFollowingTransaction"]
            }
        
        # Check if each symbol in 'ticker_symbols_to_add' is not in 'existing_ticker_symbols'
        # Define the input date as a string
        date_str = base_data['periodOfReport']
        # Parse the date string into a datetime object
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        # Convert the datetime object to a Unix timestamp (seconds since January 1, 1970)
        unix_timestamp = int(date_obj.timestamp())
        if base_data["issuerTicker"] in ticker_symbols:
            index = ticker_symbols.index(base_data["issuerTicker"])
            dates[index] = unix_timestamp
        else:
            ticker_symbols.append(base_data["issuerTicker"])
            dates.append(unix_timestamp)

        # merge base_data and entry into a new dict and append to transactions
        transactions.append({**base_data, **entry})
    except Exception as e:
        print(f"error in api.py line 239 => {e}")
        continue

  return transactions

# create a simplified list of all transactions per filing 
# with just a handful of data points, e.g. reporting person, shares sold, etc.
def flatten_filings(filings):
  unflattened_list = list(map(flatten_filing, filings))
  return [item for sublist in unflattened_list for item in sublist]

@app.route('/api/test/', methods=['GET'])
def test():
    # Define the given date
    given_date_str = "2018-01-01 05:00:00"
    given_date = datetime.datetime.strptime(given_date_str, '%Y-%m-%d %H:%M:%S')

    # Get the current date and time
    current_datetime = datetime.datetime.now()

    # Calculate the difference in days
    days_difference = (current_datetime - given_date).days

    print(f"Number of days between {given_date_str} and now: {days_difference} days")

    base_url = "https://api.finazon.io/latest/time_series?publisher=sip&ticker=AAPL&interval=1d&start_at=978307200"
    headers = {'Authorization': f"apikey {os.getenv('FINAZON_KEY')}"}

    MAX_PAGE_SIZE = 1000
    all_datas = []

    # Handle pagination
    for page in range((days_difference + MAX_PAGE_SIZE - 1) // MAX_PAGE_SIZE):
        offset = page * MAX_PAGE_SIZE
        limit = min(MAX_PAGE_SIZE, days_difference - offset)

        print(page, limit)
        conn = http.client.HTTPSConnection("api.finazon.io")
        conn.request("GET", f"{base_url}&page={page+1}&page_size={MAX_PAGE_SIZE}", headers=headers)
        res = conn.getresponse()
        data = res.read()

        # Parse the JSON string
        data_dict = json.loads(data.decode("utf-8"))
        
        # Extract the "data" field and append to all_datas
        all_datas.extend(data_dict["data"])
        if(len(data_dict["data"]) < MAX_PAGE_SIZE):
                        break

    all_datas = all_datas[:days_difference]

    for item in all_datas:
        # Convert to a datetime object
        date_object = datetime.datetime.utcfromtimestamp(item['t'])
        # Format the date as a string
        formatted_date = date_object.strftime('%Y-%m-%d %H:%M:%S')
        item['t'] = formatted_date

    df = pd.DataFrame(all_datas)
    
    return df.to_html()