FROM python:3.11-slim
WORKDIR /app
RUN pip install --quiet fastapi uvicorn python-multipart
COPY api/ /app/api/
COPY data/ /app/data/
COPY tests/ /app/tests/
EXPOSE 8000
CMD ["python3", "-m", "uvicorn", "api.wave410_fusion:handler", "--host", "0.0.0.0", "--port", "8000"]
