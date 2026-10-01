# Azure AI Search Python Course

This project is a collection of small Python examples for Azure AI Search. It starts with a traditional text-search index and progresses through document upload, hotel data indexing, blob indexers, embeddings, vector search, hybrid search, and semantic search.

The examples use the Azure SDK for Python and load configuration from a local `.env` file. They are scripts rather than a single application, so run them from the project directory in the order described below.

## What You Will Learn

- Create, inspect, and delete Azure AI Search indexes.
- Define searchable, filterable, sortable, facetable, complex, and geographic fields.
- Upload JSON documents directly with `SearchClient`.
- Build a hotel index from `hotels-small.json`.
- Connect an Azure Blob Storage container to an indexer.
- Generate Azure OpenAI embeddings and store them in JSON.
- Configure HNSW vector search profiles and vector fields.
- Compare simple text, vector, hybrid, and semantic search.
- Use scoring profiles, semantic configurations, CORS options, and Rich console output.

## Prerequisites

You need:

- Python 3.9 or later.
- An Azure AI Search service with an admin API key.
- An Azure OpenAI embedding deployment for the vector examples.
- An Azure Storage account and a blob container named `hotelscontainer` for the data source/indexer examples.

Create and activate a virtual environment from PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install azure-search-documents azure-core python-dotenv rich openai
```

## Configuration

Create a `.env` file in the project root. Do not commit this file because it contains secrets.

```dotenv
AZURE_AI_SEARCH_API_ENDPOINT=https://<search-service-name>.search.windows.net
AZURE_AI_SEARCH_API_KEY=<azure-ai-search-admin-key>
AZURE_AI_SEARCH_INDEX_NAME=text-sample-index
AZURE_AI_SEARCH_HOTEL_INDEX_NAME=hotels-index

AZURE_OPENAI_API_KEY=<azure-openai-key>
AZURE_OPENAI_API_VERSION=2024-10-21
AZURE_OPENAI_API_EMBEDDING_ENDPOINT=https://<openai-resource-name>.openai.azure.com/
AZURE_OPENAI_API_EMBEDDING_DEPLOYMENT=<embedding-deployment-name>

AZURE_STORAGE_CONNECTION_STRING=<storage-connection-string>
```

The text examples use `AZURE_AI_SEARCH_INDEX_NAME`. The hotel examples use `AZURE_AI_SEARCH_HOTEL_INDEX_NAME`. The vector scripts currently use the literal index name `azure-ai-search-vector-index6`, so create that index or update the `index_name` constant in those scripts.

## Data Files

- `text-sample.json`: small text documents with `id`, `title`, `category`, and `content` fields.
- `text-sample-embeddings.json`: generated copy of `text-sample.json` with `titleVector` and `contentVector` fields.
- `hotels-small.json`: hotel records used by the hotel index and blob indexer examples.

## Running the Examples

Run every command from the repository root with the virtual environment activated:

```powershell
python .\script-name.py
```

### Text Index and Basic Search

Run these first for the `text-sample.json` workflow:

| Script | Default action | Required configuration |
| --- | --- | --- |
| `azure_ai_search_index_crud.py` | Creates `AZURE_AI_SEARCH_INDEX_NAME` with text fields, the `MyProfile` scoring profile, CORS, and semantic configuration. | Search endpoint, key, text index name |
| `azure_ai_search_upload_json_data.py` | Reports the current document count. Uncomment `upload_documents()` in the main block to upload `text-sample.json`. | Search endpoint, key, text index name |
| `azure_ai_search_simple.py` | Runs a simple search for `gateway` using scoring profile `MyProfile`. | Search endpoint, key, text index name |
| `azure_ai_search_clear_index_data.py` | Reports the hotel index count. Uncomment `_clear_index_documents_with_wait()` to delete hotel documents. | Search endpoint, key, hotel index name |

`azure_ai_search_index_crud.py` also contains `delete_index()` and `show_all_index()`. Uncomment the function you want to run and comment out the current default call before executing the file.

Example sequence:

```powershell
python .\azure_ai_search_index_crud.py
python .\azure_ai_search_upload_json_data.py
python .\azure_ai_search_simple.py
```

Illustrative output:

```text
Index `text-sample-index` created successfully.
Upload result: [<IndexingResult key=1 succeeded=True>, ...]
Search Results - Total: 2
 Document ID  Title                 Category     Content                         @Search.Score
 1            API gateway patterns  Architecture ...                             2.41
```

### Hotel Data and Indexers

The hotel workflow uses a richer schema with nested `address` and `rooms` fields, multilingual analyzers, filters, facets, geo points, and semantic configuration.

| Script | Default action | Required configuration |
| --- | --- | --- |
| `azure_ai_search_upload_hoetel_data.py` | Uploads `hotels-small.json` to the configured hotel index. Uncomment `_create_index()` first when the index does not exist. | Search endpoint, key, hotel index name |
| `azure_ai_search_datasource.py` | Creates the `hotels-datasource` connection for the `hotelscontainer` blob container. | Search endpoint, key, storage connection string |
| `azure_ai_search_indexer.py` | Creates the `hotels-indexer`, which reads a JSON array from the data source and targets `hotels-index`. | Search endpoint, key; matching data source/index |
| `azure_ai_search_clear_index_data.py` | Gets the hotel document count by default; can clear all documents in batches. | Search endpoint, key, hotel index name |

Typical output:

```text
Documents uploaded successfully: [<IndexingResult key=1 succeeded=True>, ...]
Data source connection created successfully. hotels-datasource
Indexer hotels-indexer created successfully.
Index `hotels-index` document count: 50
```

The indexer script intentionally targets the literal names `hotels-index`, `hotels-indexer`, and `hotels-datasource`. Keep those names aligned with the hotel index and data source created by the other scripts.

### Embeddings and Vector Search

Run the vector workflow in this order:

```powershell
python .\azure_ai_search_embedding_data.py
python .\azure_ai_search_vector_index_crud.py
python .\azure_ai_search_upload_vector_json_data.py
python .\azure_ai_search_vector_search.py
python .\azure_ai_search_hybrid_search.py
python .\azure_ai_search_semantic_hybrid_search.py
```

| Script | Default action |
| --- | --- |
| `azure_ai_search_embedding_data.py` | Calls the Azure OpenAI embedding deployment for titles and content, then writes `text-sample-embeddings.json`. |
| `azure_ai_search_vector_index_crud.py` | Creates `azure-ai-search-vector-index6` with 1,536-dimensional title and content vector fields, an HNSW algorithm, scoring profile, and semantic configuration. Uncomment `_delete_index()` to remove it. |
| `azure_ai_search_upload_vector_json_data.py` | Uploads `text-sample-embeddings.json` using `SearchClient`. Uncomment the buffered sender function to try batched upload instead. |
| `azure_ai_search_vector_search.py` | Embeds `tools for software development` and performs a vector-only search, returning the top two results. |
| `azure_ai_search_hybrid_search.py` | Combines keyword search for `scalable storage solutions` with a vector query and returns the top two results. |
| `azure_ai_search_semantic_hybrid_search.py` | Runs semantic text search for a storage best-practices question using `my-semantic-config`. |

Illustrative output:

```text
Embedding exported successfully to ...\text-sample-embeddings.json
Index `azure-ai-search-vector-index6` created successfully.
Documents uploaded successfully.
Top 2 Search Results for Query: `tools for software development`
 Id  Title                  Category        @SearchScore
 3   Developer tools        Software        0.82
 1   API gateway patterns   Architecture    0.76
```

Scores and matching documents vary with the embedding model, index contents, and Azure AI Search ranking behavior. The semantic script prints `@search.rerankerScore` when Azure returns it.

## Concepts Demonstrated

### Index schema design

`SearchIndex` defines the document contract. `SimpleField` is used for keys and structured values, while `SearchableField` enables full-text search. Fields can also be filterable, sortable, facetable, multilingual, collections, complex objects, or `GeographyPoint` values.

### Ranking and semantic search

Scoring profiles increase the influence of selected fields, such as `content` or hotel `description`. Semantic configurations identify title, keyword, and content fields so Azure AI Search can rerank text results using meaning and document structure.

### Vector search

The vector index stores 1,536-dimensional embeddings in `titleVector` and `contentVector`. Its HNSW configuration provides approximate nearest-neighbor search, and `VectorizedQuery` supplies the query vector.

### Hybrid search

Hybrid search submits both `search_text` and `vector_queries`, allowing lexical matching and semantic similarity to contribute to the result set.

### Indexers and data sources

The data source connects Azure AI Search to Blob Storage. The indexer reads the JSON array from the `hotelscontainer` container and populates `hotels-index` without direct document uploads from Python.

## Operational Notes

- All scripts call `load_dotenv()`, so `.env` must be in the current working directory or an ancestor directory.
- Most scripts catch Azure errors and write detailed logs to `app.log`.
- `azure_ai_search_indexer.py` currently prints the endpoint and API key during startup. Avoid sharing that terminal output and remove those debug prints before using the script in a shared environment.
- Delete or clear indexes carefully. These examples perform real Azure operations and may incur service or model usage charges.