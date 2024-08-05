import uvicorn

from app import create_app
from fastapi import FastAPI
from app.api import router as root_router

app = create_app()






if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)