import aioredis
import uvicorn
import json
from fastapi import FastAPI, APIRouter, routing
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from auth.router import auth_router, user_router
from posts.router import router as post_router
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://redis:6379")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")



routers = APIRouter(prefix="/api/v1")

routers.include_router(auth_router)
routers.include_router(user_router)
routers.include_router(post_router)


app.include_router(routers)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Social Network api",
        version="0.0.1",
        description="",
        routes=app.routes,
    )

    for route in app.routes:
        if isinstance(route, routing.APIRoute):
            bodyField = route.body_field
            if bodyField:
                modelSchema = bodyField.type_.schema_json()
                if modelSchema:
                    jsonModelSchema = json.loads(modelSchema)
                    if "examples" in jsonModelSchema:
                        examples = jsonModelSchema["examples"]
                        for method in route.methods:
                            if method == "POST":
                                openapi_schema["paths"][route.path]["post"][
                                    "requestBody"
                                ]["content"]["application/json"]["examples"] = examples
                            elif method == "PUT":
                                openapi_schema["paths"][route.path]["put"][
                                    "requestBody"
                                ]["content"]["application/json"]["examples"] = examples

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, host="0.0.0.0", reload=True)
