"""here we define tools that are needed by an agent
"""
from langchain.agents import load_tools
from langchain.agents.tools import Tool
from langchain.utilities import PythonREPL
from pydantic import BaseModel, Field
from langchain import LLMMathChain,SerpAPIWrapper
from langchain.tools import ShellTool
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    HumanMessage,
    SystemMessage
)
import json
import requests
from langchain.chains import LLMChain 
from  langchain.prompts import PromptTemplate
from typing import List
import streamlit as st
import yfinance as yf
from yahooquery import Ticker
import os
from dotenv import load_dotenv
import openai
from openai import ChatCompletion
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import SystemMessage, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Defining schema for llm math chain as an example
class CalculatorInput(BaseModel):
    question: str = Field()

# class FhirObservationInput(BaseModel):
#     input_data: List[str] = Field(description="should be a list, with hypothesis data and pateint ID")

class FhirObservationInput(BaseModel):
    input_data: str = Field(description="hypothesis data")

class CreatePatientSummaryInput(BaseModel):
    pass



class Tools():

    def __init__(self,llm) :
        self.llm = llm

        self.tools = [
            Tool(
            name="Terminal",
            description="A terminal. Use this to execute shell commands on this MacOS machine. Input should be a valid shell command. For example, `ls`.",
            func=self.shell_tool()
            ),
            Tool(
               name="python_repl",
               description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...)`.",
                func=self.python_repl()
            ),
            Tool(
                name="Search",
                func=self.search_tool(),
                description="useful for when you need to answer questions about current events, use it only to get TICKER data. Input should be the company name. For example, `Apple`.",
            ),
            Tool(
                name="Company news",
                func=self.get_company_news,
                description="Use this to get news about a company. Input should be the company name. For example, `Apple`.",
            )
            ,
            Tool(
                name="Get Stock history",
                func=self.get_stock_data,
                description="Get historical market data for a company stock given ticker symbol, example input `AAPL`",
                

            ),
            Tool(
                name="Get Stock Analysis",
                func=self.get_stock_analysis,
                description="Get stock analysis for a company stock given ticker symbol, example input `AAPL`",
                return_direct=True

            )

        ]

    def shell_tool(self):
        shell_tool = ShellTool()
        
        #have to retun constructor
        return shell_tool.run

    def python_repl(self):
        python_repl = PythonREPL()
        
        return python_repl.run

    def search_tool(self):
        """Use this function to ONLY seach the web for getting TICKER SYMBOLS. Input should be the company name. For example, `Apple`."""
        search = SerpAPIWrapper()
        return search.run

    def get_company_news(self,company_name):
        """Use this funciton ONLY to get company news. Input should be the company name. For example, `Apple`."""
        params = {
            "engine": "google",
            "tbm": "nws",
            "q": company_name,
            "api_key": os.environ["SERPAPI_API_KEY"],
        }

        response = requests.get('https://serpapi.com/search', params=params)
        data = response.json()

        filename="app/assets/investment.txt"
        news = data.get('news_results')

        if news:
            self.write_news_to_file(news, filename)
        
        else:
            print("No news found.")



    def write_news_to_file(self,news, filename):
        with open(filename, 'w') as file:
            for news_item in news:
                if news_item is not None:
                    title = news_item.get('title', 'No title')
                    link = news_item.get('link', 'No link')
                    date = news_item.get('date', 'No date')
                    file.write(f"Title: {title}\n")
                    file.write(f"Link: {link}\n")
                    file.write(f"Date: {date}\n\n")


    def get_stock_evolution(self,company_name, period="1y"):
        # Get the stock information
        company_name = "GUJTHEM.BO"
        stock = yf.Ticker(company_name)

        # Get historical market data
        hist = stock.history(period=period)

        # Convert the DataFrame to a string with a specific format
        data_string = hist.to_string()

        # Append the string to the "investment.txt" file
        with open("app/assets/investment.txt", "a") as file:
            file.write(f"\nStock Evolution for {company_name}:\n")
            file.write(data_string)
            file.write("\n")

        return hist


    def get_financial_statements(self,ticker):
        # Create a Ticker object
        ticker = "GUJTHEM.BO"
        company = Ticker(ticker)

        # Get financial data
        balance_sheet = company.balance_sheet().to_string()
        cash_flow = company.cash_flow(trailing=False).to_string()
        income_statement = company.income_statement().to_string()
        valuation_measures = str(company.valuation_measures)  # This one might already be a dictionary or string

        # Write data to file
        with open("app/assets/investment.txt", "a") as file:
            file.write("\nBalance Sheet\n")
            file.write(balance_sheet)
            file.write("\nCash Flow\n")
            file.write(cash_flow)
            file.write("\nIncome Statement\n")
            file.write(income_statement)
            file.write("\nValuation Measures\n")
            file.write(valuation_measures)


    def get_stock_data(self, company_ticker):


        hist = self.get_stock_evolution(company_ticker)
        self.get_financial_statements(company_ticker)
        return hist

    def get_stock_analysis(self,company_ticker):
        with open("app/assets/investment.txt", "r") as file:
            content = file.read()[:14000]
        chat = ChatOpenAI(temperature=0, model_name='gpt-4', request_timeout=120)

        template = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                content=(
                    """Write a detailed investment thesis to answer
                    the user request. Provide numbers to justify
                    your assertions, a lot ideally. Always provide
                    a recommendation to buy the stock of the company
                    or not given the information available. 
                    Never mention something like this:
                    However, it is essential to consider your own risk
                    tolerance, financial goals, and time horizon before
                    making any investment decisions. It is recommended
                    to consult with a financial advisor or do further
                    research to gain more insights into the company's 
                    fundamentals and market trends. The user already knows that"""
                )
            ),
            HumanMessagePromptTemplate.from_template("This is ticker symbol {ticker},this is news {news}"),
            ]
        )

        response = chat(template.format_messages(ticker=company_ticker, news=content))

        return response.content
    
    def list_tools(self):
        return self.tools
    
