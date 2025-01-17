FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file to optimize caching
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /app/models

COPY ./src ./src
COPY ./data ./data

ENV PYTHONPATH=/app/src

ARG OPENAI_API_KEY
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
EXPOSE 8000

CMD ["uvicorn", "chat_web:app", "--host", "0.0.0.0", "--port", "8000"]
