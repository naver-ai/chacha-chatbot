from os import path, getcwd
from time import perf_counter

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from starlette.responses import HTMLResponse, FileResponse
from starlette.staticfiles import StaticFiles
from re import compile

from backend.routers import chat

app = FastAPI()

app.include_router(chat.router, prefix="/api/v1/chat")

##########################################################

asset_path_regex = compile("\.[a-z][a-z0-9]+$")

static_frontend_path = path.join(getcwd(), "frontend/dist")
if path.exists(static_frontend_path):
    @app.get("/{rest_of_path:path}", response_class=HTMLResponse)
    def redirect_frontend_nested_url(*, rest_of_path: str):

        if len(asset_path_regex.findall(rest_of_path)) > 0:
            # This is a static asset file path.
            return FileResponse(path.join(static_frontend_path, rest_of_path))
        else:
            return HTMLResponse(
                status_code=200,
                content=open(path.join(static_frontend_path, "index.html")).read()
            )


    app.mount("/", StaticFiles(directory=static_frontend_path, html=True), name="static")
    print("Compiled static frontend file path was found. Mount the file.")

#############################################


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    # or logger.error(f'{exc}')
    print(request, exc_str)
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


origins = [
    "http://localhost:3000",
    "localhost:3000",
    "http://localhost:8000",
    "localhost:8000",
    "http://localhost:8888",
    "localhost:8888",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-processing-time", "X-request-id", "X-context-id"]
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = perf_counter()
    response = await call_next(request)
    end = perf_counter()
    response.headers["X-processing-time"] = str(end - start)
    return response