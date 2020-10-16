FROM python:3
WORKDIR /usr/app/

COPY . /usr/app/

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "run.py" ]
