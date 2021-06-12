FROM python:3.6

ENV FLASK_APP run.py

COPY run.py config.py requirements.txt ./

RUN pip install -r requirements.txt

EXPOSE 5001

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5001"]