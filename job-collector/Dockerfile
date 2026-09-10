FROM python:3.10-slim
WORKDIR /collector
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py", "--interval", "3600"]
