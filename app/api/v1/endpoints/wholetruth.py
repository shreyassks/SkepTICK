from fastapi import APIRouter
from dotenv import load_dotenv
from pydantic import BaseModel

from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import SystemMessage, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
import json

load_dotenv()
router = APIRouter()


class WholeTruthRequest(BaseModel):
    age: int


def read_DB(db_name: str) -> dict:
    with open(f'app/database/{db_name}.json', 'r', encoding='utf-8') as f:
        result = json.load(f)
    return result


def analyse_single_thesis(chat, thesis: str, age: int) -> str:
    template = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                content=(
                    "You are a financial advisor. Your job is to help people against misinformations about financial topics."
                    "You are talking to a person who is watching a financial influencer on youtube. You will receive part of transcript of the video where influencer is making a thesis about investment"
                    "You have to present counter-thesis to the person in brief."
                    "Take into account that the person is not an expert in finance and is not familiar with financial terms."
                    "Take into account risk profile of person based on his age, here the age is {age}."
                    "Assume younger people are more risk tolerant and older people are more risk averse."
                    "Dont add any information or disclaimers outside of core counter-analysis."
                )
            ),
            HumanMessagePromptTemplate.from_template("{text}"),
        ]
    )

    response = chat(template.format_messages(text=thesis, age=age))

    return response.content


@router.get("/wholetruth")
def wholetruth() -> dict:
    age = 28
    """Iterate over all theses in DB and generate counter-theses for each of them."""
    all_thesis = read_DB("thesis")
    analysis_dict = {}

    chat = ChatOpenAI(temperature=0, model_name='gpt-4', request_timeout=120)
    for thesis in all_thesis["thesis_theoretical"]:
        thesis_str = list(thesis.values())[0]
        analysis = analyse_single_thesis(chat, thesis_str, age)
        analysis_dict[list(thesis.keys())[0]] = thesis_str, analysis

    return analysis_dict
