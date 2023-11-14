import yfinance as yf
import pandas as pd
from datetime import date, timedelta

def multipler(n): return (2/(n+1))

def calculate_signals(data):
    # Calculate the MACD or Fast Line
    upperMulti, lowerMulti = multipler(26), multipler(12)
    
    upperEWM = list(data.iloc[:26]['Adj Close'])
    LowerEWM = list(data.iloc[:12]['Adj Close'])

    uEWM = sum(upperEWM) / 26
    lEWM = sum(LowerEWM) / 12
    
    for i in range(12, len(data)):
        adjClose = data.iloc[i]['Adj Close']
        lEWM = (adjClose * lowerMulti) + (lEWM * (1 - lowerMulti))
        LowerEWM.append(lEWM)
        if i >= 26:
            uEWM = (adjClose * upperMulti) + (uEWM * (1 - upperMulti))
            upperEWM.append(uEWM)
    
    data['MACD'] = [round(LowerEWM[i] - upperEWM[i], 6) for i in range(len(upperEWM))]
    
    # Calculate the signal line
    smallMulti = multipler(9)
    
    smallEWM = list(data.iloc[:9]['MACD'])
    
    sEWM = sum(smallEWM) / 9
    
    for i in range(9, len(data)):
        newLEWM = (data.iloc[i]['MACD'] * smallMulti) + (sEWM * (1 - smallMulti))
        smallEWM.append(newLEWM)
        sEWM = newLEWM
        
    data['Signal'] = smallEWM
    
    return data

def position_analysis(data, transaction, balance):
    
    if transaction['Buy'].iloc[-1] == False:
        # If singal is less than MACD then we buy
        if data['MACD'].iloc[-1] > data['Signal'].iloc[-1]:
            Quantity = balance / data['Adj Close'].iloc[-1]

            return({'Price': data['Adj Close'].iloc[-1], 'Quantity': Quantity, 'Buy': True, 
                    'Sell': False}, 0)
            
    else:
        # If price is getting too close to buying point then sell or Singnal more than MACD
        if data['Adj Close'].iloc[-1] < transaction['Price'].iloc[-1] or data['MACD'].iloc[-1] < data['Signal'].iloc[-1]:
            balance += (transaction['Quantity'].iloc[-1] * data['Adj Close'].iloc[-1])
            
            return({'Price': data['Adj Close'].iloc[-1], 'Quantity': transaction['Quantity'].iloc[-1], 
                    'Buy': False, 'Sell': True}, balance)
    
    return(None, balance)

'''Function to calaculate the total balance after exectution'''
def work_equity(balance, transaction):
    if transaction['Buy'].iloc[-1] == True:
        return print(transaction['Quantity'].iloc[-1] * transaction['Price'].iloc[-1])
    else:
        return print(balance)

'''Main Functions for Running all Processes'''
def controller(end_date, start_date, ticker):
    # Get the data and organise it appropriatly 
    data = calculate_signals(yf.download(ticker, start_date, end_date))
    # Create the tranaction list for trading, show all transactions made
    tempData = [[1, 1, False, False]]
    transaction = pd.DataFrame(tempData, columns=['Price', 'Quantity', 'Buy', 'Sell'])
    balance = 100
    
    # Loops through the data and performs for each of them
    for x in range(26, len(data)):
        trans, balance = position_analysis(data.iloc[:x], transaction, balance)
        # If no return then we haven't done anything to the data, if there is we edit the transactions
        if trans is not None:
            transaction = pd.concat([transaction, pd.DataFrame(trans, index=[0])]).reset_index(drop = True)
    
    print(transaction)
    work_equity(balance, transaction)
    
    return

ticker = 'CANE'
end_date = date.today()
start_date = end_date - timedelta(days = 250)
controller(end_date, start_date, ticker)
