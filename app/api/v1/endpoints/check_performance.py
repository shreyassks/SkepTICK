import json
import os.path

from fastapi import APIRouter
from app.helper import financial_advisor
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from pydantic import BaseModel
from app.agents.agent import ActionAgent
from langchain.llms import OpenAI
from langchain import PromptTemplate
from pathlib import Path
from langchain.callbacks.streaming_stdout_final_only import (
    FinalStreamingStdOutCallbackHandler,
)
#------------------------
import pandas as pd 
import yfinance as yf 
import ta 
from backtesting import Backtest, Strategy
from backtesting.lib import crossover 

class SMAcross(Strategy):
      def init(self):
          close=self.data.Close 
          self.sma1 = self.I(ta.trend.sma_indicator, pd.Series(close), 50)
          self.sma2 = self.I(ta.trend.sma_indicator, pd.Series(close), 100)
    
      def next(self):
          if crossover(self.sma1,self.sma2):
            self.buy()
          elif crossover(self.sma2,self.sma1):
            self.sell()

df=yf.download('GUJTHEM.BO', period='3y')
bt = Backtest(df, SMAcross, cash=10000, commission=0.002, exclusive_orders=True) 
output = bt.run()           
#bt.plot()

nifty_50_data = yf.download('^NSEI', period='3y')
nifty_50_cagr = ((nifty_50_data.tail(1)['Close'].values[0] / nifty_50_data.head(1)['Close'].values[0]) ** (1 / 3) - 1)*100
strategy_cagr = output['Return (Ann.) [%]']

plot_nifty_cagr = ((plot_df.tail(1)['Nifty50'].values[0] / plot_df.head(1)['Nifty50'].values[0]) ** (1 / 3) - 1)*100


def save_graph(output, nifty_50_data, strategy_cagr, nifty_50_cagr):
    strategy_series = output['_equity_curve'][['Equity']].reset_index().rename(columns={'index': 'Date', 'Equity': 'Strategy'})
    nifty_50_series = nifty_50_data['Close'].reset_index().rename(columns={'Close': 'Nifty50_Index'})
    plot_df = nifty_50_series.merge(strategy_series, how='inner', on=['Date'])
    plot_df.index=plot_df['Date']
    plot_df['Nifty50_lag']=plot_df['Nifty50_Index'].shift(1)
    plot_df['Nifty50_return']=(plot_df['Nifty50_Index']-plot_df['Nifty50_Index'].shift(1))/plot_df['Nifty50_Index'].shift(1)
    
    # Calculate Nifty 50 investment values
    initial_investment = 10000
    investment_values_nifty = [initial_investment]
    for i in range(1, len(plot_df)):
        investment_value = investment_values_nifty[i - 1] * (1 + plot_df['Nifty50_return'][i])
        investment_values_nifty.append(investment_value)
    plot_df['Nifty50'] = investment_values_nifty
    
    plt.switch_backend('Agg')
    plt.figure(figsize=(12, 8))
    
    # Plot Nifty 50 and Strategy returns
    plt.plot(plot_df['Date'], plot_df['Nifty50'], label='Nifty 50')
    plt.plot(plot_df['Date'], plot_df['Strategy'], label='Strategy')
    
    # Add CAGR text annotations
    plt.annotate(f"Nifty 50 CAGR: {nifty_50_cagr:.2f}%", 
                 xy=(plot_df['Date'].iloc[1], plot_df['Nifty50'].iloc[1]),
                 xytext=(10, 10), textcoords='offset points', color='blue')
    plt.annotate(f"Strategy CAGR: {strategy_cagr:.2f}%", 
                 xy=(plot_df['Date'].iloc[1], plot_df['Strategy'].iloc[1]),
                 xytext=(10, -20), textcoords='offset points', color='orange')
    
    plt.xlabel("Date")
    plt.ylabel("Investment Value")
    plt.title("Nifty 50 and Strategy Performance")
    plt.grid()
    plt.legend()
    
    image_name = "Performance_image1.png"
    plt.savefig(image_name)
    plt.close()  # Close the plot to free resources
    
    return image_name


def save_graph(output, nifty_50_data):
    strategy_series=output['_equity_curve'][['Equity']].reset_index().rename(columns={'index':'Date', 'Equity':'Strategy'})
    nifty_50_series=nifty_50_data['Close'].reset_index().rename(columns={'Close':'Nifty50_Index'})
    plot_df=nifty_50_series.merge(strategy_series, how='inner', on=['Date'])
    plot_df.index=plot_df['Date']
    plot_df['Nifty50_lag']=plot_df['Nifty50_Index'].shift(1)
    plot_df['Nifty50_return']=(plot_df['Nifty50_Index']-plot_df['Nifty50_Index'].shift(1))/plot_df['Nifty50_Index'].shift(1)
    initial_investment = 10000
    investment_values = [initial_investment]
    for i in range(1, len(plot_df)):
        investment_value = investment_values[i - 1] * (1 + plot_df['Nifty50_return'][i])
        investment_values.append(investment_value)
    # Add investment values to the DataFrame
    plot_df['Nifty50'] = investment_values
    plt.switch_backend('Agg')
    plot_df[['Nifty50', 'Strategy']].plot(grid=True, figsize=(12, 8))
    #plt.title(f"{company_name} Stock Price")
    plt.xlabel("Date")
    plt.ylabel("Investment over the time")
    #directory = os.path.join(Path(__file__).parent.parent.parent.parent.parent, "chrome-plugin/images")
    #image_name = directory + "/Performance_image1.png"
    image_name = "Performance_image1.png"
    plt.savefig(image_name)
    return image_name

#------------------------

load_dotenv()
router = APIRouter()


class TipsRequest(BaseModel):
    username: str


def fetch_db(username):
    with open(f'app/database/claims.json', 'r', encoding='utf-8') as f:
        claims = json.load(f)
    company_name = list(claims.keys())
    return company_name[0]


def create_graph(history, company_name):
    hist_selected = history[['Open', 'Close']]

    plt.switch_backend('Agg')
    hist_selected.plot(kind='line')
    plt.title(f"{company_name} Stock Price")
    plt.xlabel("Date")
    plt.ylabel("Stock Price")

    directory = os.path.join(Path(__file__).parent.parent.parent.parent.parent, "chrome-plugin/images")
    image_name = directory + "/image1.png"
    plt.savefig(image_name)
    return image_name


@router.get("/stock_tips")
def stock_tips():
    company_name = "Gujarat Themis Biosyn Ltd"  # fetch_db("Rahul Jain")
    # role of agent is to get investment thesis based on factual data from news source, stock history, balance sheets

    llm = OpenAI(temperature=0,streaming=True,callbacks=[FinalStreamingStdOutCallbackHandler()],verbose=True)
    action_agent = ActionAgent(llm)
    
    prompt_template = PromptTemplate.from_template(
        "Goal 1) Given the compnay name {company_name}, get news articles about the company using Company news tool"
        "Goal 2) Get the ticker or trading symbol for {company_name}"
        "Goal 3) Once you have ticker symbol, get the stock history for the company using Stock history tool"
        "Goal 4) Use the same ticker symbol, to get stock analysis for the company using Stock analysis tool"
    )

    prompt = prompt_template.format(company_name=company_name)
    
    investment_thesis=action_agent.run(prompt)
    print("OUTPUT FROM AGENT", investment_thesis)

    history = financial_advisor(company_name)
    stock_chart = create_graph(history, company_name)
    return stock_chart, investment_thesis
