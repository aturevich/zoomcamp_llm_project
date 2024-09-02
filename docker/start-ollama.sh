#!/bin/bash

# Start Ollama in the background
ollama serve &

# Wait for Ollama to start
sleep 10

# Pull the llama2 model
ollama pull llama2

# Keep the container running
wait
