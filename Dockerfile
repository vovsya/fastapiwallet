FROM python:3

WORKDIR wallet_app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "wallet_project.main:wallet_app", "--host", "0.0.0.0", "--port", "8000"]
