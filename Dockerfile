FROM PROJECT_NAME-runtime:latest

WORKDIR /code

# RUN apt-get update && apt-get install -y wkhtmltopdf
# RUN apt-get update

# COPY . /code
COPY . .

RUN pip3 install pipenv && pipenv lock && pipenv install --deploy --system




CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]