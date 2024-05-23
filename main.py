import redis.asyncio as redis
from fastapi import FastAPI
from src.routes import contacts,auth,users
from fastapi_limiter import FastAPILimiter

from src.conf.config import settings

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(contacts.router, prefix='/api')
app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')

origins = [
    "*"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """
        Initializes the application on startup.

        This function is called when the application starts and initializes the rate limiter.
    """
    r = await redis.Redis(host=settings.redis_host, 
                          port=settings.redis_port, 
                          password=settings.redis_password, 
                          db=0,
                          encoding="utf-8",
                          decode_responses=True)
    await FastAPILimiter.init(r)

@app.get('/')
def read_root():
    """
        The root endpoint.

        This function handles the GET request at the root of the application.

        :return: A welcome message.
        :rtype: dict
    """
    return {'message':'helloworld'}
