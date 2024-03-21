FROM python:3.10.13-slim AS compile-image

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade -r /requirements.txt


FROM python:3.10.13-slim AS build-image

COPY --from=compile-image /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN mkdir /app
WORKDIR /app
CMD [ "python", "./test.py"]