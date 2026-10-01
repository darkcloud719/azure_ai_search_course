import os, json, logging, sys
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.models import QueryType, QueryCaptionType, QueryAnswerType, VectorizedQuery
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndex,
    SimpleField,
    SearchFieldDataType,
    SearchableField,
    IndexingParameters,
    SearchIndexerDataSourceConnection,
    IndexingParametersConfiguration,
    CorsOptions,
    SearchIndexer,
    ScoringProfile,
    TextWeights,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch
)
from typing import List
from rich import print as pprint
from rich.logging import RichHandler
from rich.table import Table
from rich.console import Console
from pathlib import Path
from openai import AzureOpenAI

load_dotenv()

service_endpoint = os.getenv("AZURE_AI_SEARCH_API_ENDPOINT")
api_key = os.getenv("AZURE_AI_SEARCH_API_KEY")
index_name = "hotels-index"
indexer_name = "hotels-indexer"
data_source_name = "hotels-datasource"

print(service_endpoint)
print(api_key)

if not service_endpoint:
    raise ValueError("AZURE_AI_SEARCH_API_ENDPOINT environment variable is not set.")
if not api_key:
    raise ValueError("AZURE_AI_SEARCH_API_KEY environment variable is not set.")

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

def _create_indexer():

    try:
        configuration = IndexingParametersConfiguration(
            parsing_mode="jsonArray",
            query_timeout=None
        )

        parameters = IndexingParameters(configuration=configuration)

        indexer = SearchIndexer(
            name=indexer_name,
            data_source_name=data_source_name,
            target_index_name=index_name,
            parameters=parameters
        )

        with SearchIndexerClient(endpoint=service_endpoint, credential=AzureKeyCredential(api_key)) as search_indexer_client:
            search_indexer_client.create_indexer(indexer)
            pprint(f"[green]Indexer {indexer_name} created successfully.[/green]")
    except Exception as e:
        pprint(f"[red]Error creating indexer: {e}[/red]")
        logger.error(f"Error creating indexer: {e}")

def _delete_indexer():

    try:
        with SearchIndexerClient(endpoint=service_endpoint, credential=AzureKeyCredential(api_key)) as search_indexer_client:
            search_indexer_client.delete_indexer(indexer_name)
            pprint(f"[green]Indexer {indexer_name} deleted successfully.[/green]")
    except Exception as e:
        pprint(f"[red]Error deleting indexer: {e}[/red]")
        logger.error(f"Error deleting indexer: {e}")

    
if __name__ == "__main__":
    _create_indexer()
