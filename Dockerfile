# ----------- STEP 1: Build Dependencies  -----------

# Select base image - Python 3.10
FROM python:3.10-slim AS requirements-stage

# Set working directory to `app`
WORKDIR /app

# Install psycopg2 and required libs before installing the requirements and clean intermediate files
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install Poetry in this Docker stage.
RUN pip install poetry uvicorn

# Copy the pyproject.toml and poetry.lock filess into working directory
COPY ./pyproject.toml ./poetry.lock* /app/

# Generate the requirements.txt file.
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes \
    && pip install --no-cache-dir --upgrade -r requirements.txt \
    && rm -rf /tmp/*

# ----------- STEP 2: Build Image  -----------
FROM python:3.10-slim

WORKDIR /app

# Copy dependencies installed in the requirements stage
COPY --from=requirements-stage /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Copy application code to container's working directory
COPY . .

# Expose the port where the app would run on
EXPOSE 8080

# Run FastAPI using uvicorn web server (src/main.py => app = FastAPI())
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
