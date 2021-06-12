FROM python:3.6

ENV FLASK_APP run.py

COPY run.py config.py requirements.txt ./
COPY static static
COPY templates templates

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["flask", "run", "--host", "0.0.0.0",  "--port", "5000"]