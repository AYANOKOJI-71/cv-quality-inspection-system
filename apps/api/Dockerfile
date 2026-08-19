FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY apps/api/src ./apps/api/src
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.5.1+cpu \
    && pip install --no-cache-dir .
COPY data/fixtures/.gitkeep ./data/fixtures/.gitkeep
RUN mkdir -p runtime
EXPOSE 4800
CMD ["uvicorn", "inspection.main:app", "--host", "0.0.0.0", "--port", "4800"]
