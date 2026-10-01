import os
import logging

from typing import List
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchFieldDataType,
    ScoringProfile,
    SearchableField,
    CorsOptions,
    ScoringProfile,
    ComplexField,
    TextWeights,
    SearchField,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SearchSuggester
)
from dotenv import load_dotenv
from rich import print as pprint
from rich.logging import RichHandler

load_dotenv()

service_endpoint = os.getenv("AZURE_AI_SEARCH_API_ENDPOINT")
api_key = os.getenv("AZURE_AI_SEARCH_API_KEY")

index_name = os.getenv("AZURE_AI_SEARCH_INDEX_NAME")

if not service_endpoint:
    raise ValueError(
        "AZURE_AI_SEARCH_API_ENDPOINT environment variable is not set."
    )

if not api_key:
    raise ValueError(
        "AZURE_AI_SEARCH_API_KEY environment variable is not set."
    )

if not index_name:
    raise ValueError(
        "AZURE_AI_SEARCH_INDEX_NAME environment variable is not set."
    )


def setup_logger():
    """Create and configure the application logger.

    Parameters:
        None. The logger name, level, and output destinations are defined by
        this module.

    Returns:
        logging.Logger: A logger that writes messages to the Rich console and
        to ``app.log``. Existing handlers are reused to avoid duplicates.

    Main logic:
        Configure a console handler and a formatted file handler when the
        logger has not already been configured, then return the logger.
    """

    logger = logging.getLogger("azure-ai-search")
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Console handler
    console_handler = RichHandler(
        rich_tracebacks=True,
        show_time=True,
        show_level=True,
        show_path=False
    )

    console_handler.setLevel(logging.INFO)

    # File handler
    file_handler = logging.FileHandler(
        "app.log",
        mode="a",
        encoding="utf-8"
    )

    file_handler.setLevel(logging.INFO)

    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()


def delete_index():
    """Delete the configured index from the Azure AI Search service.

    Parameters:
        None. The service endpoint, API key, and index name come from the
        module-level environment configuration.

    Returns:
        None. The result is printed and logged; errors are caught and logged.

    Main logic:
        Create a ``SearchIndexClient``, delete the configured index, and
        report success or failure.
    """

    try:
        with SearchIndexClient(endpoint=service_endpoint, credential=AzureKeyCredential(api_key)) as index_client:
            index_client.delete_index(index_name)

            pprint(f"[green]Index `{index_name}` deleted successfully.")
            logger.info(f"Index `{index_name}` deleted successfully.")
    except Exception as e:
        pprint(f"[red]Failed to delete index `{index_name}`: {e}")
        logger.exception(f"Failed to delete index `{index_name}`: {e}")

def create_index():
    """Create the configured Azure AI Search index and its schema.

    Parameters:
        None. The service endpoint, API key, and index name come from the
        module-level environment configuration.

    Returns:
        None. The result is printed and logged; errors are caught and logged.

    Main logic:
        Define the index fields, semantic settings, scoring profile, and CORS
        options, then submit the resulting ``SearchIndex`` to Azure.
    """

    try:
        with SearchIndexClient(endpoint=service_endpoint, credential=AzureKeyCredential(api_key)) as index_client:
            fields = [
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SearchableField(name="title", type=SearchFieldDataType.String),
                SearchableField(name="category", type=SearchFieldDataType.String, filtrable=True),
                SearchableField(name="content", type=SearchFieldDataType.String)
            ]

            semantic_config = SemanticConfiguration(
                name="my-semantic-config",
                prioritized_fields=SemanticPrioritizedFields(
                    title_field=SemanticField(field_name="title"),
                    keywords_fields=[SemanticField(field_name="category")],
                    content_fields=[SemanticField(field_name="content")]
                    
                )
            )

            semantic_search = SemanticSearch(configurations=[semantic_config])

            scoring_profiles: List[ScoringProfile] = []
            scoring_profile = ScoringProfile(
                name="MyProfile",
                text_weights=TextWeights(weights={"content": 2.0})
            )

            scoring_profiles.append(scoring_profile)

            cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
            # suggester = SearchSuggester(name="sg", source_fields=["title","content"])

            index = SearchIndex(
                name=index_name,
                fields=fields,
                scoring_profiles=scoring_profiles,
                cors_options=cors_options,
                # suggesters=suggester,
                semantic_search=semantic_search
            )

            index_client.create_index(index)
            pprint(f"[green]Index `{index_name}` created successfully.")
            logger.info(f"Index `{index_name}` created successfully.")
    except Exception as e:
        pprint(f"[red]Failed to create index `{index_name}`: {e}")
        logger.exception(f"Failed to create index `{index_name}`: {e}")

def show_all_index():
    """List and display all indexes in the Azure AI Search service.

    Parameters:
        None. The service endpoint and API key come from the module-level
        environment configuration.

    Returns:
        None. Index names are printed and logged; errors are caught and logged.

    Main logic:
        Create a ``SearchIndexClient``, retrieve all index names, and display
        them as a comma-separated list.
    """

    try:
        with SearchIndexClient(endpoint=service_endpoint, credential=AzureKeyCredential(api_key)) as index_client:
            indexes = list(index_client.list_index_names())
            pprint(f"[cyan]Indexes:[/cyan] {', '.join(indexes)}")
            logger.info(f"Indexes: {', '.join(indexes)}")
    except Exception as e:
        pprint(f"[red]Failed to retrieve indexes: {e}")
        logger.exception(f"Failed to retrieve indexes: {e}")

if __name__ == "__main__":
    # delete_index()
    create_index()
    # show_all_index()

