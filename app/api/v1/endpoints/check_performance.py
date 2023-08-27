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
import matplotlib.pyplot as plt
import pandas as pd 
import yfinance as yf 
import ta 
from backtesting import Backtest, Strategy
from backtesting.lib import crossover 

load_dotenv()
router = APIRouter()

class PerfRequest(BaseModel):
        ticker: str
        duration: int 
        implement_strat: str

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

class SMAcross1(Strategy):
      def init(self):
          close=self.data.Close 
          self.sma1 = self.I(ta.trend.sma_indicator, pd.Series(close), 10)
          self.sma2 = self.I(ta.trend.sma_indicator, pd.Series(close), 100)
    
      def next(self):
          if crossover(self.sma1,self.sma2):
            self.buy()
          elif crossover(self.sma2,self.sma1):
            self.sell()

class SMAcross2(Strategy):
      def init(self):
          close=self.data.Close 
          self.sma1 = self.I(ta.trend.sma_indicator, pd.Series(close), 20)
          self.sma2 = self.I(ta.trend.sma_indicator, pd.Series(close), 30)
    
      def next(self):
          if crossover(self.sma1,self.sma2):
            self.buy()
          elif crossover(self.sma2,self.sma1):
            self.sell()

class RSI_Strategy(Strategy):
    def init(self):
        close = self.data.Close
        self.rsi = self.I(ta.momentum.RSIIndicator, pd.Series(close), 14)
    
    def next(self):
        if self.rsi[-1] > 70:  # Overbought condition
            self.sell()
        elif self.rsi[-1] < 30:  # Oversold condition
            self.buy()            


class BollingerBandsStrategy(Strategy):
    def init(self):
        close = self.data.Close
        self.bollinger = self.I(ta.volatility.BollingerBands, pd.Series(close), window=20)
    
    def next(self):
        if cross(self.data.Close, self.bollinger.bollinger_l):
            self.buy()
        elif cross(self.bollinger.bollinger_h, self.data.Close):
            self.sell()

class BreakoutStrategy(Strategy):
    def init(self):
        high = self.data.High
        low = self.data.Low
        close = self.data.Close
        self.atr = self.I(ta.volatility.AverageTrueRange, high, low, close, window=14)
    
    def next(self):
        if self.data.Close[-1] > self.data.Close[-2] + self.atr[-1]:
            self.buy()
        elif self.data.Close[-1] < self.data.Close[-2] - self.atr[-1]:
            self.sell()

def save_graph(output, nifty_50_data, strategy_cagr, nifty_50_cagr, implement_strat):
    strategy_series = output['_equity_curve'][['Equity']].reset_index().rename(columns={'index': 'Date', 'Equity': 'Strategy'})
    nifty_50_series = nifty_50_data['Close'].reset_index().rename(columns={'Close': 'Nifty50_Index'})
    plot_df = nifty_50_series.merge(strategy_series, how='inner', on=['Date'])
    plot_df.index=plot_df['Date']
    plot_df['Nifty50_lag']=plot_df['Nifty50_Index'].shift(1)
    plot_df['Nifty50_return']=(plot_df['Nifty50_Index']-plot_df['Nifty50_Index'].shift(1))/plot_df['Nifty50_Index'].shift(1)
    
    # Calculate Nifty 50 investment values
    initial_investment = 100000
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

    directory = os.path.join(Path(__file__).parent.parent.parent.parent.parent, "chrome-plugin/images")
    image_name = directory + f"/{implement_strat}.png"    
    plt.savefig(image_name)
    plt.close()  # Close the plot to free resources    
    return image_name

@router.post("/check_performance")
def breakdown(request: PerfRequest):
    ticker = request.ticker
    duration = request.duration
    implement_strat = request.implement_strat

    strategies = {
    'SMAcross': SMAcross,
    'RSI_Strategy': SMAcross1,
    'BreakoutStrategy': SMAcross2,
    'BollingerBandsStrategy': SMAcross1
    }
    image_name=''
    nifty_50_cagr=''
    strategy_cagr=''
    volatility_percent='' 
    sharpe_ratio='' 
    sortino_ratio=''
    max_drawdown_percent=''
    #print('Strat:',strategies[implement_strat])
    try:
        selected_strategy = strategies[implement_strat]
        df=yf.download(ticker, period=f'{duration}y')
        bt = Backtest(df, selected_strategy, cash=100000, commission=0.002, exclusive_orders=True) 
        output = bt.run()           
        nifty_50_data = yf.download('^NSEI', period=f'{duration}y')
        nifty_50_cagr = ((nifty_50_data.tail(1)['Close'].values[0] / nifty_50_data.head(1)['Close'].values[0]) ** (1 / 3) - 1)*100
        strategy_cagr = output['Return (Ann.) [%]']

        image_name=save_graph(output, nifty_50_data, strategy_cagr, nifty_50_cagr, implement_strat)

        volatility_percent = output['Volatility (Ann.) [%]']
        sharpe_ratio = output['Sharpe Ratio']
        sortino_ratio = output['Sortino Ratio']
        max_drawdown_percent = output['Max. Drawdown [%]']

    except Exception as e:
        print("An error occurred:", e)
    return {"image_name": image_name, "nifty_50_cagr": nifty_50_cagr, "strategy_cagr":strategy_cagr,
            "volatility_percent": volatility_percent, "sharpe_ratio": sharpe_ratio, "sortino_ratio":sortino_ratio,
            "max_drawdown_percent": max_drawdown_percent}
