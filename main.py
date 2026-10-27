from fastapi import FastAPI

import models
from database import Base, engine
from routers import products, users


Base.metadata.create_all(engine)

app = FastAPI()
app.include_router(products.router)
app.include_router(users.router)


@app.get("/")
def root():
    return {"message": "ERP is working"}