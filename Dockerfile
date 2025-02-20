FROM python:3.13-slim
EXPOSE 8081
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--config", "gunicorn_config.py", "app:app"]

ENV PYTHONUNBUFFERED=1

ENV AWS_REGION=""
ENV AWS_Q1=""
ENV TEAMS_WEBHOOK=""
ENV AWS_ACCESS_KEY_ID=""
ENV AWS_SECRET_ACCESS_KEY=""