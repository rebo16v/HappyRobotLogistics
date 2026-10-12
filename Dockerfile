
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the tms folder so the directory structure is preserved
COPY tms/ ./tms/

# Run uvicorn referencing the tms module
CMD ["uvicorn", "tms.main:app", "--host", "0.0.0.0", "--port", "8080"]
