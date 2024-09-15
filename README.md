# D&D 5e RAG Pipeline

This project implements a Retrieval-Augmented Generation (RAG) pipeline for answering questions about Dungeons & Dragons 5th Edition (D&D 5e) using Elasticsearch for document retrieval and Ollama for text generation.

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
   make docker-up
   ```

5. Wait for all services to be ready. You can check the status with:
   ```
   docker-compose -f docker/docker-compose.yml ps
   ```

## Usage

### Running the RAG Pipeline

To interact with the D&D 5e SRD Assistant, you can use the web interface or the command-line interface.

#### Web Interface

1. Open a web browser and navigate to `http://localhost:3000`
2. Use the chat interface to ask questions about D&D 5e

#### Command-line Interface

To run the RAG pipeline from the command line:

```
pipenv run python -m src.pipeline.rag_pipeline
```

This will process a sample question about D&D 5e and output the answer along with retrieval metrics.

### Monitoring

A monitoring dashboard is available at `http://localhost:3000/dashboard`. This dashboard provides insights into system usage, query performance, and user feedback.

## Development

### Code Formatting

To format the code using Black:

```
make format
```

### Linting

To run the linter:

```
make lint
```

### Running Tests

To run the test suite:

```
make test
```

### Updating Dependencies

After installing new packages, update the Pipfile.lock:

```
make requirements
```

## Components

- **Elasticsearch**: Used for storing and retrieving D&D 5e documents.
- **Ollama**: Local LLM service for text generation.
- **FastAPI**: Backend API for handling requests and running the RAG pipeline.
- **React**: Frontend web application for user interaction.
- **PostgreSQL**: Database for storing interaction logs and feedback.

## Retrieval Method Evaluation

We have evaluated four different retrieval methods:

1. Keyword Search
2. BM25 Search
3. Semantic Search
4. Hybrid Search

Semantic Search significantly outperforms other methods, showing the highest average and maximum relevance scores. For detailed evaluation results, see `src/evaluation/retrieval_evaluation.py`.

| Method         | Average Relevance | Max Relevance | Min Relevance |
|----------------|-------------------|---------------|---------------|
| Semantic Search| 0.4146            | 0.5031        | 0.3629        |
| BM25 Search    | 0.1500            | 0.4164        | -0.0027       |
| Keyword Search | 0.1432            | 0.4164        | 0.0258        |
| Hybrid Search  | 0.1187            | 0.4164        | -0.0494       |

Semantic Search significantly outperforms other methods, showing the highest average and maximum relevance scores.

1. Ensure all Docker containers are running: `docker-compose -f docker/docker-compose.yml ps`
2. Check the logs of specific services: `docker-compose -f docker/docker-compose.yml logs [service_name]`
3. Ensure the `.env` file is correctly set up in the project root
4. Make sure you're running commands from within the activated Pipenv shell: `pipenv shell`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

