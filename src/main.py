from fastapi import FastAPI
from src.routes.routes import router
from src.utils.database import Base, engine


app = FastAPI()
app.include_router(router)

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Hello world!"}
