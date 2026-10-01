import os
import logging
from typing import List
import json
from pathlib import Path
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from dotenv import load_dotenv
from rich import print as pprint 
from rich.logging import RichHandler
from rich.table import Table
from rich.console import Console

load_dotenv()

service_endpoint = os.getenv("AZURE_AI_SEARCH_API_ENDPOINT")
api_key = os.getenv("AZURE_AI_SEARCH_API_KEY")
index_name = os.getenv("AZURE_AI_SEARCH_INDEX_NAME")

if not service_endpoint:
    raise ValueError("AZURE_AI_SEARCH_API_ENDPOINT is not set.")

if not api_key:
    raise ValueError("AZURE_AI_SEARCH_API_KEY is not set.")

if not index_name:
    raise ValueError("AZURE_AI_SEARCH_INDEX_NAME is not set.")


def setup_logger():

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    console_handler = RichHandler()
    console_handler.setLevel(logging.WARNING)

    file_handler = logging.FileHandler("app.log", mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()

def upload_documents():

    try:
        path = Path.cwd().joinpath("text-sample.json")
        with open(path, "r", encoding="utf-8") as f:
            input_data = json.load(f)

        with SearchClient(service_endpoint, index_name, AzureKeyCredential(api_key)) as search_client:
            result = search_client.upload_documents(documents=input_data)
            pprint(f"[green]Upload result: {result}[/green]")
            logger.info(f"Upload result: {result}")

    except Exception as e:
        pprint(f"[red]Upload failed: {e}[/red]")
        logger.error(f"Upload failed: {e}")

def get_document_count_from_index():

    try:
        with SearchClient(service_endpoint, index_name, AzureKeyCredential(api_key)) as search_client:
            result = search_client.get_document_count()
            pprint(f"[green]Document count: {result}[/green]")
            logger.info(f"Document count: {result}")

    except Exception as e:
        pprint(f"[red]Failed to get document count: {e}[/red]")
        logger.error(f"Failed to get document count: {e}")

if __name__ == "__main__":
    # upload_documents()
    get_document_count_from_index()
        


