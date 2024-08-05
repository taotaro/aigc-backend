# import pathlib
from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI
import asyncio
# from fastapi_cache import FastAPICache
# from fastapi_cache.backends.redis import RedisBackend
from motor.motor_asyncio import AsyncIOMotorClient
# from redis.asyncio import RedisCluster, Redis
# from redis.asyncio.cluster import ClusterNode
from starlette.middleware.cors import CORSMiddleware
# from starlette.staticfiles import StaticFiles

from app.config import Settings, get_settings
# from app.libs.controller.kafka import BinaryOwlConsumer
# from app.libs.custom import cus_print
# from app.models import BaseDBModel

__all__ = (
    'create_app',
)


def create_app():
    
    app = FastAPI()
    register_routers(app)
    mongo_client = initialize_mongodb_client()
    # init_db(mongo_client)
    @app.on_event("startup")
    async def on_startup():
        print("Starting up")
        await init_db(mongo_client)
    # app.add_middleware(
    #     CORSMiddleware,
    #     allow_credentials=True,
    #     allow_methods=["*"],
    #     allow_headers=["*"],
    #     expose_headers=["*"],
    # )
    # print("Startup complete")
    return app


def register_routers(app: FastAPI):
    from app.api import router as root_router
    from app.api.common import router as main_router

    app.include_router(root_router)
    app.include_router(main_router)


def initialize_mongodb_client():
    settings = get_settings()
    print(f"Connecting to MongoDB at {settings.MONGODB_URI}:{settings.MONGODB_PORT}")
    return AsyncIOMotorClient(
        host=get_settings().MONGODB_URI,
        port=get_settings().MONGODB_PORT,
        username=get_settings().MONGODB_USERNAME,
        password=get_settings().MONGODB_PASSWORD,
        authSource=get_settings().MONGODB_AUTHENTICATION_SOURCE
    )


async def init_db(mongo_client: AsyncIOMotorClient):
    import app.models.common as common_models
    settings = get_settings()
    print(f"Initializing Beanie with database {settings.MONGODB_DB} and models {common_models.__all__}")
    
    await init_beanie(
        database=getattr(mongo_client, get_settings().MONGODB_DB),
        document_models=[
            *load_models_class(common_models),
        ]
    )


def load_models_class(module):
    return [
        getattr(module, model) for model in module.__all__ if
        model.endswith('Model') and not model.endswith('ViewModel')
    ]


# async def init_payment_network_configure():
#     import json
#     from app.models.payment.manual_pay import PaymentNetworkModel
#     if await PaymentNetworkModel.count():
#         return
#     with open(f'{pathlib.Path(__file__).resolve().parent}/statics/payment_network_configure.json', 'r') as f:
#         await PaymentNetworkModel.insert_many([
#             PaymentNetworkModel(**d) for d in json.load(f).values()
#         ])
