FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create necessary directories
RUN mkdir -p Life_OS/01_Inbox Life_OS/02_Library Life_OS/03_Decision_Matrix Life_OS/04_Brain

CMD ["python", "server.py"]
