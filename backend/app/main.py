import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.config import settings
from app.core.database import init_db
from app.workers.orchestrator import InverterOrchestrator
from app.workers.aggregator import MetricsAggregator
from app.api.v1.endpoints import router as rest_router
from app.api.v1.websocket import router as ws_router

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("solarhub.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Iniciando almacenamiento SQLite...")
    await init_db()

    aggregator = MetricsAggregator()
    aggregator.start()
    app.state.aggregator = aggregator

    orchestrator = InverterOrchestrator(settings.inverters)
    orchestrator.start()
    app.state.orchestrator = orchestrator

    logger.info(f"SolarHub iniciado con {len(orchestrator.workers)} workers activos.")

    yield

    # Shutdown
    logger.info("Deteniendo workers Modbus...")
    await orchestrator.stop()

    logger.info("Deteniendo agregador de métricas...")
    await aggregator.stop()
    logger.info("Shutdown finalizado correctamente.")


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rest_router)
app.include_router(ws_router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
