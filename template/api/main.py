from __future__ import annotations

from fastapi import FastAPI

from api.routers import context, health, media, products, search, variants

app = FastAPI(title="Product KB API", version="0.1.0")
app.include_router(health.router)
app.include_router(products.router)
app.include_router(variants.router)
app.include_router(media.router)
app.include_router(context.router)
app.include_router(search.router)
