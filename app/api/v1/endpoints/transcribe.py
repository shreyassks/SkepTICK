import json
from pytube import extract
from fastapi import APIRouter

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from pydantic import BaseModel
load_dotenv()

router = APIRouter()


class TranscribeRequest(BaseModel):
    video_url: str


def transcribe(video_url):
    """
    Given YouTube Video URL as input, returns the transcription
    :param video_url:
    :return: <str> transcribed text and author name
    """
    youtube = YouTube(video_url)
    author = youtube.author

    transcript = ""
    video_id = extract.video_id(video_url)
    srt = YouTubeTranscriptApi.get_transcript(video_id)

    for line in srt:
        transcript = transcript + " " + line["text"]
    return author, transcript


def extract_entities(transcript):
    """
    Takes YouTube transcript as input, extracts stock name, claims, theoretical and quantitative thesis
    :param transcript:
    :return: writes JSON files for theoretical and quantitative parts
    """
    chat = ChatOpenAI(temperature=0, model_name='gpt-4', request_timeout=120)
    messages = [
        SystemMessage(content="You are a Financial Analyst. Your task is to identify the company stock and the context of claims made on the stock by a Financial Influencer. \
                      Please separate out the theoretical and quantitative analysis from the response. Report the response in JSON format with keys company_name, claims, \
                      theoretical_analysis and quantitative_analysis."),
        HumanMessage(content=transcript)
    ]
    response = chat(messages)
    formatted_output = eval(response.content)

    claims, thesis = {}, {"thesis_theoretical": [], "thesis_quantitative": []}
    claims[formatted_output["company_name"]] = formatted_output["claims"]

    for i, text in enumerate(formatted_output["theoretical_analysis"]):
        thesis["thesis_theoretical"].append({f"Thesis{i}": text})

    for i, text in enumerate(formatted_output["quantitative_analysis"]):
        thesis["thesis_quantitative"].append({f"Thesis{i}": text})
    return claims, thesis


def store_json(response1, response2, username):
    """
    Writes two JSON files for Claims and Thesis
    :param username: YouTube video author
    :param response1: claims
    :param response2: thesis
    """
    response1["username"], response2["username"] = username, username

    with open(f'app/database/claims.json', 'w', encoding='utf-8') as f:
        json.dump(response1, f, ensure_ascii=False, indent=4)

    with open(f'app/database/thesis.json', 'w', encoding='utf-8') as f:
        json.dump(response2, f, ensure_ascii=False, indent=4)


@router.post("/transcribe/breakdown")
def breakdown(request: TranscribeRequest):
    username, transcript = transcribe(request.video_url)
    claims, thesis = extract_entities(transcript)
    store_json(claims, thesis, username)
    return {"claims": claims, "thesis": thesis}
