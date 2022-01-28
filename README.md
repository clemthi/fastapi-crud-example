# FastAPI CRUD example
I made this little example to show how easily you make a REST api with basic CRUD operation with [FastAPI](https://fastapi.tiangolo.com) and [SQLAlchemy](https://www.sqlalchemy.org/).

## Setup dev environement
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt 
```

## Run the API
```
python -m uvicorn main:app
```