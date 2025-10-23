from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import HttpUrl, Field, DirectoryPath, RedisDsn, SecretStr
from typing import Annotated
from pydantic.types import StringConstraints
from pathlib import Path


class _s3Settings(BaseSettings):
    host: str = Field(alias="S3_HOST")
    access_key: str = Field(alias="S3_ACCESS_KEY")
    secret_key: str = Field(alias="S3_SECRET_KEY")



class Settings(BaseSettings):
    """
    This class stores the settings for this microservice
    """

    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", validate_default=False, env_nested_delimiter=""
    )

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

    db_host: str = Field(default="postgres", alias="DB_HOST")
    db_port: int = Field(5432, alias="DB_PORT")
    db_user: str = Field(alias="DB_USER")
    db_password: SecretStr = Field(alias="DB_PASS")
    db_name: str = Field(default="wisdom", alias="DB_NAME")

    allow_overwriting_models: bool = Field(alias="MODEL_ALLOW_OVERWRITE", default=False)
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

    use_s3_storage: bool = Field(default=False, alias="USE_S3_STORAGE")


    s3_endpoint: str | None = Field(default=None, alias="S3_ENDPOINT")
    s3_access_key: str | None = Field(default=None, alias="S3_ACCESS_KEY")
    s3_secret_key: str | None = Field(default=None, alias="S3_SECRET_KEY")
    s3_bucket_name: str | None = Field(default=None, alias="S3_BUCKET_NAME")

    redis_dsn: RedisDsn | None = Field(default=None, alias="REDIS_DSN")
    
