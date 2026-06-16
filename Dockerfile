FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8080 \
    READ_ONLY_DEMO=true \
    ALLOW_FILE_UPLOADS=false \
    PERSIST_UPLOADED_FILES=false \
    ENABLE_LLM_COMMENTARY=false

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY app.py ./
COPY data/sample ./data/sample
COPY docs ./docs
COPY NOTICE ./

RUN pip install --upgrade pip && pip install .

EXPOSE 8080

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8080", "--server.headless=true"]
