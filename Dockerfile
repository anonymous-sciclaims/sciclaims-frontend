FROM python:3.8
LABEL health_claims_demo.authors="rortega@expert.ai"

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY /app /app

EXPOSE 9043

CMD ["streamlit", "run", "/app/src/run.py", "--server.baseUrlPath", "/health_claims/", "--server.port", "9043", "--server.enableXsrfProtection", "false", "--server.enableCORS", "false"]
