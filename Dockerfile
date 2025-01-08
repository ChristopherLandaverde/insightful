
FROM python:3.11-slim

WORKDIR /app

COPY app/ .


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


COPY . .

RUN adduser --disabled-password --gecos '' appuser

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD curl --fail http://localhost:8000/ || exit 1


RUN ls -R /app


# Run the tests from the correct path







EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


