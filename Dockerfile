FROM python:3.11.9
WORKDIR /app
COPY requirements.txt ./
RUN pip install -U pip &&\
    pip install -r requirements.txt --no-cache-dir
COPY . .
RUN chmod a+x run_bot.sh
ENTRYPOINT ["/app/run_bot.sh"]