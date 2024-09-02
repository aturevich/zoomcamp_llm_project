# D&D 5e RAG Pipeline

This project implements a Retrieval-Augmented Generation (RAG) pipeline for answering questions about Dungeons & Dragons 5th Edition (D&D 5e) using Elasticsearch for document retrieval and Ollama for text generation.

## Project Structure

```
llm_project/
├── src/
│ ├── ingestion/
│ │ └── elasticsearch_ingestion.py
│ ├── models/
│ │ └── ollama_interface.py
│ ├── evaluation/
│ │ └── metrics.py
│ ├── pipeline/
│ │ └── rag_pipeline.py
│ └── utils/
│ └── config.py
├── data/
│ └── dnd_srd/
├── docker/
│ └── docker-compose.yml
├── .env
├── Pipfile
├── Pipfile.lock
└── README.md
```

## Prerequisites

- Python 3.10+
- Docker and Docker Compose
- Pipenv

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/llm_project.git
   cd llm_project
   ```

2. Install dependencies:
   ```
   pipenv install
   ```

3. Create a `.env` file in the project root with the following content:
   ```
   OLLAMA_URL=http://localhost:11434/api/generate
   OLLAMA_MODEL=mistral:latest
   ```

4. Start the Docker containers:
   ```
   docker-compose -f docker/docker-compose.yml up -d
   ```

5. Activate the virtual environment:
   ```
   pipenv shell
   ```

## Running the RAG Pipeline

To run the RAG pipeline:

```
python -m src.pipeline.rag_pipeline
```

This will process a sample question about D&D 5e and output the answer along with retrieval metrics.

## Components

- **Elasticsearch**: Used for storing and retrieving D&D 5e documents.
- **Ollama**: Local LLM service for text generation.
- **RAG Pipeline**: Combines document retrieval and text generation to answer questions.

## Current Status

- The RAG pipeline is functional and can answer questions about D&D 5e.
- Document retrieval is working, but relevance scores are currently low.
- The Ollama API is successfully integrated and generating responses.

## Known Issues and Future Improvements

- Low relevance scores in document retrieval. Need to improve the indexing and retrieval process.
- Context is currently limited to 1000 characters. May need adjustment for more comprehensive answers.
- Response time from Ollama API is around 53 seconds. Performance optimization might be necessary.
- Expand the knowledge base to cover more D&D 5e topics.

## Retrieval Method Evaluation

We have evaluated four different retrieval methods for our D&D 5e SRD Assistant:

1. Keyword Search
2. BM25 Search
3. Semantic Search
4. Hybrid Search

### Results Summary

| Method         | Average Relevance | Max Relevance | Min Relevance |
|----------------|-------------------|---------------|---------------|
| Semantic Search| 0.4146            | 0.5031        | 0.3629        |
| BM25 Search    | 0.1500            | 0.4164        | -0.0027       |
| Keyword Search | 0.1432            | 0.4164        | 0.0258        |
| Hybrid Search  | 0.1187            | 0.4164        | -0.0494       |

Semantic Search significantly outperforms other methods, showing the highest average and maximum relevance scores.

### Next Steps

Based on these results, we plan to:

1. Implement Semantic Search as the primary retrieval method.
2. Investigate the underperformance of the Hybrid Search method.
3. Expand our evaluation metrics to include precision@k and NDCG.
4. Increase the number and diversity of test questions.
5. Optimize the weighting in the Hybrid Search method.

For more details on the evaluation process and results, see `src/evaluation/retrieval_evaluation.py`.

## Troubleshooting

If you encounter issues with environment variables not loading correctly, ensure that:
1. The `.env` file is in the project root directory.
2. You're running the script from within the activated Pipenv shell.
3. The `python-dotenv` package is installed in your Pipenv environment.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Your chosen license]