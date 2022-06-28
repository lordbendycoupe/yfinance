import json
import yfinance as yf
import numpy as np
import pandas as pd
import datetime as date
import boto3
from boto3.dynamodb.conditions import Key





    
class stockdata:
    
    def __init__(self):
        dclient = boto3.resource('dynamodb', region_name = "us-west-1")
        tablename = 'yml'
        self.table = dclient.Table(tablename)
        
        
    
    def init_system(self, event):
        response = self.table.put_item(
            Item={
                'ticker': event['ticker']
                
        }
            
        )
        
            
        return { 'body': event['ticker'] + ' use tasktype=get'}
        
        
    
    
    def get_event(self, event):
        response = self.table.get_item (
            Key = {
                'ticker' : event['ticker']
            }
        )
        if 'Item' in response: 
            return response['Item']
        else:
            return {
                'statusCode': '404',
                'body': 'not found'
            }
    
    
    
    
    def query_data(self,event):
        response = self.table.query(
            
            KeyConditionExpression=Key('ticker').eq(event['ticker']),
           # ExpressionAttributeValues = {
               # ':ticker': event['ticker']},
            
            ProjectionExpression= 's_date, #s', 
            ExpressionAttributeNames = {'#s': 'signal'},
    
          
        )
        return {
            'statusCode': '200',
            'body': response
        }
        #print(response['Items'])
        
        
 

           
    def update_data(self, df, event):
        for index, row in df.iterrows():
            date = str(index).split()
            ninedayopen = str(index).split()
            ninedayclose = str(index).split()
           # signal = df['signal']
            Item = {'ticker': event['ticker'], 's_date': date}
            for i in range(len(row)):
                Item[df.columns[i]] = {'S':str(row[i])}
            self.table.put_item(Item=Item)
        
        return Item




def lambda_handler(event, context):
    stockobject = stockdata()
    if event['tasktype'] == "create":
        createresult = stockobject.init_system(event['data'])
        return createresult
        
    elif event['tasktype'] == "get":
        response = stockobject.get_event(event['data'])
        value = response['ticker']
        gticker = yf.Ticker(value)
        ghistory = gticker.history(period = '3mo')
        df = sma_crossover_signal(ghistory, 9, 26)
        updated = stockobject.update_data(df, event['data'])
        #return updated
        refresh = stockobject.query_data(event['data'])
        return refresh
        
        

        
# Original 
def sma_crossover_signal(df, short_window, long_window):
    MA_short = f'{short_window}-day SMA'
    MA_long = f'{long_window}-day SMA'
    df[MA_short] = df['Close'].rolling(short_window).mean()
    df[MA_long] = df['Close'].rolling(long_window).mean()
    df['signal'] = np.where(df[MA_short] > df[MA_long],1,0)
    

    
    return df
    
    
