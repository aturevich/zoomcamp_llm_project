# RAG Application Project: D&D 5e SRD Assistant

## Objective
Build an end-to-end Retrieval-Augmented Generation (RAG) application using the Dungeons & Dragons 5th Edition System Reference Document (SRD) content.

## Project Overview
We're creating a D&D 5e SRD assistant that can answer questions and provide information about the game rules, mechanics, and content using RAG technology.

## Current Progress
- [x] Selected D&D 5e SRD as the dataset
- [x] Created an ingestion pipeline using Python to index the content into Elasticsearch
- [x] Successfully indexed 986 documents with nested objects (tables and lists)
- [x] Implemented the core RAG flow
- [x] Integrated with Ollama LLM (using Mistral model)
- [x] Created a basic interface for the application (command-line script)
- [x] Set up basic monitoring (response time logging)
- [x] Implemented multiple retrieval approaches (keyword, BM25, semantic, hybrid)
- [x] Created evaluation script for retrieval methods
- [x] Evaluated and compared all retrieval methods

## Detailed Evaluation Criteria and Progress

1. Problem description (2/2 points)
   - [x] The problem is well-described and it's clear what problem the project solves

2. RAG flow (2/2 points)
   - [x] Both a knowledge base (Elasticsearch) and an LLM (Ollama with Mistral) are used in the RAG flow

3. Retrieval evaluation (2/2 points)
   - [x] Multiple retrieval approaches are evaluated
   - [x] Evaluation results are analyzed and documented

4. RAG evaluation (2/2 points)
   - [x] Evaluate multiple RAG approaches (different retrieval methods)
   - [x] Select and use the best RAG approach (implement Semantic Search as primary method)

5. Interface (2/2 points)
   - [x] Command line interface implemented
   - [x] Develop a UI (React-based web application)

6. Ingestion pipeline (2/2 points)
   - [x] Automated ingestion with a Python script

7. Monitoring (2/2 points)
   - [x] Basic response time logging implemented
   - [x] Collect user feedback
   - [x] Create a monitoring dashboard with at least 5 charts

8. Containerization (2/2 points)
   - [x] Provide Dockerfile for the main application
   - [x] Create docker-compose for all components

9. Reproducibility (2/2 points)
   - [x] Basic instructions provided in README
   - [x] Ensure dataset is easily accessible
   - [x] Specify versions for all dependencies

10. Best practices (3/3 points)
    - [x] Implement hybrid search (combining text and vector search)
    - [x] Implement document re-ranking
    - [x] Implement user query rewriting

11. Bonus: Cloud deployment (0/2 points)
    - [ ] Deploy the application to a cloud platform

## Next Steps
1. [x] Evaluate multiple retrieval approaches
2. [x] Implement Semantic Search as the primary retrieval method
3. [x] Investigate and improve Hybrid Search performance
4. [x] Expand evaluation metrics (implement precision@k and NDCG)
5. [x] Increase the number and diversity of test questions
6. [x] Improve the interface (e.g., create a web application or API)
7. [x] Enhance monitoring with user feedback collection and a comprehensive dashboard
8. [ ] Containerize the entire application
9. [x] Improve reproducibility with detailed instructions and dependency specifications
10. [x] Implement remaining best practices: document re-ranking
11. [x] Implement remaining best practices: query rewriting
12. [ ] Consider cloud deployment for bonus points

## Technologies Used
- Knowledge Base: Elasticsearch
- Ingestion: Custom Python script
- LLM: Ollama (Mistral model)
- Interface: Basic command-line script (to be improved)
- Monitoring: Basic logging (to be enhanced)
- Retrieval Methods: Keyword, BM25, Semantic, and Hybrid search implemented and evaluated
- Reranking: Implemented using SentenceTransformer model
- Query Processing: Implemented query rewriting using custom D&D synonyms and WordNet

## Notes
- Semantic Search has been selected as the primary retrieval method based on evaluation results
- Document re-ranking has been implemented and shows significant improvement in result relevance
- Query rewriting has been implemented with D&D-specific expansions and general synonyms
- Consider security improvements for Elasticsearch
- Explore options for performance optimization of Ollama API calls
- Research advanced monitoring tools suitable for the project (e.g., Grafana, Kibana)
