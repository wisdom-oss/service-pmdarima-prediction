from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import HttpUrl, Field, DirectoryPath
from typing import Annotated
from pydantic.types import StringConstraints
from pathlib import Path

class Settings(BaseSettings):
    """
    This class stores the settings for this microservice
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", validate_default=False)

    dwd_proxy_base_api: HttpUrl = Field(
        alias="DWD_PROXY_BASE_URL",
        default=HttpUrl("https://wisdom-demo.uol.de/api/dwd/v1"),
    )
    """
    The Base URL used for requests against the DWD Proxy service
    """

    dwd_station_id: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True, min_length=5, max_length=5, pattern=r"\d{5}"
        ),
    ] = Field(alias="DWD_STATION_ID")
    """
    The ID of the Station that should be used when retrieving data from the
    DWD proxy service
    """

    database_user: str = Field(alias="DB_USER")
    database_password: str = Field(alias="DB_PASS")
    database_host: str = Field(alias="DB_HOST", default="postgres")
    database_port: int = Field(alias="DB_PORT", default=5432)
    database_schema_name: str = Field(alias="DB_NAME", default="wisdom")

    allow_duplicate_models: bool = Field(alias="ALLOW_DUPLICATE_MODELS", default=False)
    device_prefix: str = Field(alias="DEVICE_PREFIX", default="urn:ngsi-ld:Device:")

    trained_model_storage_location: DirectoryPath = Field(
        alias="TRAINED_MODELS_STORAGE_DIRECTORY",
        default=Path("./.files/trained_models/"),
    )
    example_data_storage_location: DirectoryPath = Field(
        alias="EXAMPLE_DATA_STORAGE_DIRECTORY",
        default=Path("./.files/smartmeterdata/"),
    )
    result_storage_location: DirectoryPath = Field(
        alias="RESULTS_STORAGE_DIRECTORY",
        default=Path("./.files/results"),
    )
