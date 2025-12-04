FROM python:3.12

WORKDIR /app
RUN python -m venv /app/.venv

COPY requirements.txt .
RUN /app/.venv/bin/pip install --upgrade pip && \
    /app/.venv/bin/pip install -r requirements.txt

COPY scripts /app/scripts

CMD ["/app/.venv/bin/python", "scripts/import_csv.py"]