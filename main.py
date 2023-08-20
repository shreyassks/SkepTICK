from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api.root import root_router
from app.api.v1.api import v1_router
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
app.include_router(root_router, tags=["Default"])
app.include_router(v1_router, tags=["V1"])

# class Item(BaseModel):
#     username: str
#     amount: float
#     # url:str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],
)


@app.get("/whole-truth")
async def get_whole_truth():
    return {"message": "the whole truth"}


class RegisterRequest(BaseModel):
    username: str
    amount: str
    age: str


@app.post("/register")
async def register(registerRequest: RegisterRequest):
    print(registerRequest)
    return registerRequest


# @app.post("/invest")
# async def create_item(item: Item):
#     print(f"Username: {item.username}, Amount: {item.amount}")
#     return {"Username": item.username, "Amount": item.amount}


# @app.post('/register'):
# amount,
# usernmae

# # add to user.json
# #returns 200 ok


# @app.post('/transcribe'):
# youtube_url,

# # returns {}

# @app.get('wholetruth')
# @app.get('wholet')

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    print(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0")
