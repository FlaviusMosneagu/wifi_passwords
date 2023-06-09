from fastapi import FastAPI, Depends, Request, HTTPException
from starlette import status
from sqlmodel import SQLModel
from configuration.database import engine
from models.wifi import Wifi
from repository import Repository
from schemas.wifi import WifiInput
import uvicorn
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Steal saved wifi passwords with Flipper Zero on windows",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/static")
def static(request: Request, repository: Repository = Depends()):
    return templates.TemplateResponse("index.html", {"request": request, "wifis": repository.list()})


@app.post("/", status_code=status.HTTP_201_CREATED)
def create_wifis(wifi_input: WifiInput, repository: Repository = Depends()) -> object:
    response = repository.create(Wifi.from_orm(wifi_input))

    if not response:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return {
        "id": response.id
    }


@app.get("/", status_code=status.HTTP_200_OK)
def get_wifis(repository: Repository = Depends()):
    return repository.list()


@app.delete("/{wifi_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wifis(wifi_id: int, repository: Repository = Depends()):
    if not repository.delete_by_id(wifi_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


@app.get("/danger", status_code=status.HTTP_204_NO_CONTENT)
def danger_delete(repository: Repository = Depends()):
    return repository.delete_all()


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


# Start Uvicorn Server
if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
