#!/bin/sh

# Example models, change accordingly
MODELS="
llama3.2:1b
phi3:mini
qwen2.5:0.5b
"

for m in $MODELS; do
  echo "Pulling $m"
  docker-compose -f .devcontainer/coding/docker-compose.workspace.yml exec ollama ollama pull "$m"
done

for m in $MODELS; do
  echo "Pulling $m"
  podman-compose -f .devcontainer/coding/docker-compose.workspace.yml exec ollama ollama pull "$m"
done