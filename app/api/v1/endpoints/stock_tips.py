import json
from fastapi import APIRouter
from app.helper import financial_advisor
from dotenv import load_dotenv
import matplotlib.pyplot as plt

load_dotenv()

router = APIRouter()


def fetch_db(username):
    with open(f'app/database/claims.json', 'r', encoding='utf-8') as f:
        claims = json.load(f)
    company_name = claims["company_name"]
    return company_name


def create_graph(history, company_name):
    hist_selected = history[['Open', 'Close']]

    plt.switch_backend('Agg')
    hist_selected.plot(kind='line')
    plt.title(f"{company_name} Stock Price")
    plt.xlabel("Date")
    plt.ylabel("Stock Price")

    image_path = f"assets/{company_name}.png"
    plt.savefig(image_path)
    return image_path


@router.get("/stock_tips")
def stock_tips(request: TipsRequest):
    company_name = "hdfc bank"  # fetch_db(username)
    investment_thesis, history = financial_advisor(company_name)
    stock_chart = create_graph(history, company_name)
    return stock_chart, investment_thesis
