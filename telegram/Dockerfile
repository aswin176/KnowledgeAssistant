FROM python:3.12-slim
WORKDIR /app
RUN pip install python-telegram-bot httpx
COPY bot.py .
CMD ["python", "bot.py"]
