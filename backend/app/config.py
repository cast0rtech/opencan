import os
from pathlib import Path
from typing import List
import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.models.enums import DriverType


class InverterConfig(BaseModel):
    id: str = Field(..., description="Identificador único del inversor")
    name: str
    driver: DriverType
    host: str
    port: int = 502
    unit_id: int = 1
    timeout: float = 3.0
    poll_interval: float = Field(default=2.0, ge=0.5, le=60.0)
    base_address: int = 40069
    enabled: bool = True


class StorageConfig(BaseModel):
    database_url: str = "sqlite+aiosqlite:///./data/solar_metrics.db"
    retention_days: int = 30
    buffer_flush_seconds: int = 60


class Settings(BaseSettings):
    app_name: str = "SolarHub Industrial Gateway"
    debug: bool = False
    inverters: List[InverterConfig] = []
    storage: StorageConfig = StorageConfig()

    model_config = SettingsConfigDict(env_prefix="SOLAR_", env_nested_delimiter="__")

    @classmethod
    def load(cls) -> "Settings":
        config_path_env = os.environ.get("SOLAR_CONFIG_PATH")
        candidate_paths = [
            Path(config_path_env) if config_path_env else None,
            Path("config.yaml"),
            Path("../config.yaml"),
            Path("/app/config.yaml"),
        ]

        data = {}
        for p in candidate_paths:
            if p and p.exists() and p.is_file():
                with open(p, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                break

        return cls(**data)


settings = Settings.load()
