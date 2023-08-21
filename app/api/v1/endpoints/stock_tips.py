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
