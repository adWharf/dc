FROM python:3.6.5-alpine3.7
ENV PYTHONPATH /usr/src/app
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD [ "python", "dc/datacenter.py" ]
