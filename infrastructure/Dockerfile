# Usa uma imagem oficial do Python 3.13 como base
FROM python:3.13

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala o Poetry no sistema
RUN pip install poetry

# Copia os arquivos do projeto para o container
COPY ../ ./

# Instala as dependências do projeto
RUN poetry install --no-root

# Expor a porta padrão do FastAPI
EXPOSE 8000

# Comando para iniciar a API
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
