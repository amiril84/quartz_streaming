import requests
import openai
import re
import json
from openai import OpenAI
import time
import asyncio
import aiohttp
import os

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

serper_url = "https://google.serper.dev/search"

serper_headers = {
  'X-API-KEY': SERPER_API_KEY,
  'Content-Type': 'application/json'
}

client = OpenAI(api_key=OPENAI_API_KEY)

def decide(query):
    prompt = f"""I have a query {query}. Decide if you can answer this query with your pre-trained knowledge or if you need to do web search.
    Return either "search" or "complete" based on your decision."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        max_tokens=1000,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content

def complete(query):
    prompt = f"""I have a query {query}. 
    Provide a detailed and comprehensive answer to this question.
    Format the output with bullet points, paragraphs, headings, and subheadings."""
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=4096,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        stream=True
    )
    return response

def transform(query):
    prompt = f"""Here is my query {query}. To get the most accurate and comprehensive search results, 
    please break this query down into five more focused sub-queries. 
    Each sub-query should target a specific aspect or angle of the main topic, ensuring a wide range of information is covered. 
    Return only the list of new sub queries and nothing else."""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        max_tokens=1000,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content

async def async_search(query):
    async with aiohttp.ClientSession() as session:
        payload = json.dumps({"q": query})
        async with session.post(serper_url, headers=serper_headers, data=payload) as response:
            data = await response.json()
            return set(item["snippet"] for item in data["organic"][:5])

async def search(queries):
    tasks = [async_search(query) for query in queries.split("\n")]
    snippets = await asyncio.gather(*tasks)
    return set().union(*snippets)


def answer(user_query, snippets):
    prompt = f"""Provide comprehensive and detail answer to this question {user_query} 
    with the most relevant information you can find from this data: {snippets}.
    Format the output with bullet points, paragraphs, headings, and subheadings."""
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=4096,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        stream=True
    )
    return response
