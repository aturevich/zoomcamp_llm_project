#!/bin/bash

# Start Ollama in the background
ollama serve &

# Wait for Ollama to start
sleep 10

# Pull the mistral model
ollama pull mistral:latest

# Keep the container running
wait
