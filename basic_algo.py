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
