import os, json, logging, sys
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.models import QueryType, QueryCaptionType, QueryAnswerType, VectorizedQuery
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection
)
from typing import List
from rich import print as pprint
from rich.logging import RichHandler
from rich.table import Table
from rich.console import Console
from pathlib import Path
from openai import AzureOpenAI

load_dotenv()

console = Console()
service_endpoint = os.getenv("AZURE_AI_SEARCH_API_ENDPOINT")
api_key = os.getenv("AZURE_AI_SEARCH_API_KEY")
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

if not service_endpoint:
    raise ValueError("AZURE_AI_SEARCH_API_ENDPOINT environment variable is not set.")
if not api_key:
    raise ValueError("AZURE_AI_SEARCH_API_KEY environment variable is not set.")
if not connection_string:
    raise ValueError("AZURE_STORAGE_CONNECTION_STRING environment variable is not set.")

def setup_logging():

    logger = logging.getLogger(__file__)
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

logger = setup_logging()

def create_data_source_connection():
    try:
        container = SearchIndexerDataContainer(name="hotelscontainer")
        data_source_connection = SearchIndexerDataSourceConnection(
            name="hotels-datasource",
            type="azureblob",
            connection_string=connection_string,
            container=container
        )

        with SearchIndexerClient(service_endpoint, AzureKeyCredential(api_key)) as indexer_client:
            result = indexer_client.create_data_source_connection(data_source_connection)
            pprint(f"[green]Data source connection created successfully. {result.name}[/green]")
    except Exception as e:
        pprint(f"[red]Error creating data source connection: {e}[/red]")
        logger.error(f"Error creating data source connection: {e}")

def list_data_source_connections():
    try:
        with SearchIndexerClient(service_endpoint, AzureKeyCredential(api_key)) as indexer_client:
            result = indexer_client.get_data_source_connections()
            names = [ds.name for ds in result]
            pprint(f"[green]Data source connections: {', '.join(names)}[/green]")
    except Exception as e:
        pprint(f"[red]Error listing data source connections: {e}[/red]")
        logger.error(f"Error listing data source connections: {e}")

def get_data_source_connection():
    try:
        with SearchIndexerClient(service_endpoint, AzureKeyCredential(api_key)) as indexer_client:
            result = indexer_client.get_data_source_connection("hotels-datasource")
            pprint(f"[green]Data source connection details: {result}[/green]")
    except Exception as e:
        pprint(f"[red]Error getting data source connection: {e}[/red]")
        logger.error(f"Error getting data source connection: {e}")

def delete_data_source_connection():
    try:
        with SearchIndexerClient(service_endpoint, AzureKeyCredential(api_key)) as indexer_client:
            result = indexer_client.delete_data_source_connection("hotels-datasource")
            pprint(f"[green]Data source connection deleted successfully.[/green]")
    except Exception as e:
        pprint(f"[red]Error deleting data source connection: {e}[/red]")
        logger.error(f"Error deleting data source connection: {e}")

if __name__ == "__main__":
    # list_data_source_connections()
    create_data_source_connection()