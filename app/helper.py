import os
import requests
import json
import yfinance as yf
from yahooquery import Ticker
import openai
from openai import ChatCompletion
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_company_news(company_name):
    params = {
        "engine": "google",
        "tbm": "nws",
        "q": company_name,
        "api_key": os.environ["SERPAPI_API_KEY"],
    }

    response = requests.get('https://serpapi.com/search', params=params)
    data = response.json()

    return data.get('news_results')


def write_news_to_file(news, filename):
    with open(filename, 'w') as file:
        for news_item in news:
            if news_item is not None:
                title = news_item.get('title', 'No title')
                link = news_item.get('link', 'No link')
                date = news_item.get('date', 'No date')
                file.write(f"Title: {title}\n")
                file.write(f"Link: {link}\n")
                file.write(f"Date: {date}\n\n")


def get_stock_evolution(company_name, period="1y"):
    # Get the stock information
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


def get_financial_statements(ticker):
    # Create a Ticker object
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


def get_data(company_name, company_ticker, filename="app/assets/investment.txt"):
    news = get_company_news(company_name)
    if news:
        write_news_to_file(news, filename)
    else:
        print("No news found.")

    hist = get_stock_evolution(company_ticker)
    get_financial_statements(company_ticker)
    return hist


def financial_advisor(request):
    print(f"Received request: {request}")
    hist = get_stock_evolution("GUJTHEM.BO")
    return hist
