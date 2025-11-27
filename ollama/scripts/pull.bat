@echo off
REM Example models, change accordingly

set MODELS=llama3.2:1b phi3:mini qwen2.5:0.5b

for %%m in (%MODELS%) do (
  echo Pulling %%m
  docker-compose -f .devcontainer/coding/docker-compose.workspace.yml exec ollama ollama pull %%m
)
