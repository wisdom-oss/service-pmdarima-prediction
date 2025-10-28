from .. import config
from os import path
from pathlib import Path
from typing import Any

import pickle
from minio import Minio, S3Error
from pmdarima import ARIMA

from ..classes import ModelMetaData
from ..exceptions.service_error import ServiceException


class ModelStorageController(object):
    _s3_client: Minio
    _s3_bucket_name: str
    _local_storage_path: str
    _use_s3: bool = False
    _allow_overwriting_models: bool = False

    def __init__(self) -> None:
        self._allow_overwriting_models = config.allow_overwriting_models
        if config.use_s3_storage:
            self._use_s3 = True
            self._s3_bucket_name = config.s3_bucket_name
            self._s3_client = Minio(
                endpoint=config.s3_endpoint,
                access_key=config.s3_access_key,
                secret_key=config.s3_secret_key,
            )
        else:
            self._local_storage_path = config.trained_model_storage_location

    def create_training_log_path(self, training_id: str) -> str:
        log_path = path.join(self._local_storage_path, f"{training_id}.training-log")
        return log_path

    def store_model(self, model: ARIMA, meta: ModelMetaData) -> None:
        pickled_model: bytes = pickle.dumps(model)
        if self._use_s3:
            self._store_model_in_s3(meta.generate_identifier(), pickled_model)
        else:
            self._store_model_locally(meta.generate_identifier(), pickled_model, meta)
        pass

    def model_exists(self, model_id: str) -> bool:
        if self._use_s3:
            try:
                _ = self._s3_client.stat_object(self._s3_bucket_name, model_id)
                return True
            except S3Error as e:
                print(e)
                return False
        else:
            model_path = path.join(self._local_storage_path, f"{model_id}.model")
            return path.exists(model_path)

    def _store_model_locally(
        self, model_id: str, data: bytes, metadata: ModelMetaData
    ) -> None:
        model_path = path.join(self._local_storage_path, f"{model_id}.model")
        meta_path = path.join(self._local_storage_path, f"{model_id}.model_meta")

        with open(model_path, mode="xb", buffering=0) as model_file:
            byte_count = model_file.write(data)

        print(f"wrote {byte_count} bytes into {model_path}")

        with open(meta_path, mode="xt") as meta_file:
            byte_count = meta_file.write(metadata.model_dump_json())

            print(f"wrote {byte_count} bytes into {meta_path}")

    def _store_model_in_s3(self, model_id: str, data: bytes) -> None:
        if not self._s3_allow_model_writing(model_id):
            raise ServiceException(
                "",
                409,
                "Model Overwriting not Allowed",
                "The model you tried to train and save",
            )

    def _s3_allow_model_writing(self, model_id: str) -> bool:
        try:
            _ = self._s3_client.stat_object(self._s3_bucket_name, model_id)
            return self._allow_overwriting_models
        except S3Error as e:
            print(e)
            return False
        pass

    def load_model_by_id(self, model_id: str) -> ARIMA:
        meta_path = path.join(self._local_storage_path, f"{model_id}.model")
        with open(meta_path, mode="rb") as meta_file:
            raw = meta_file.read()

        raw_model = pickle.loads(raw)
        if not isinstance(raw_model, ARIMA):
            raise TypeError("Un-pickled file does not contain ARIMA model")

        return raw_model

    def load_model_from_path(self, path: Path) -> ARIMA:
        pass

    def load_metdata_for_model(self, model_id: str) -> ModelMetaData:
        meta_path = path.join(self._local_storage_path, f"{model_id}.model_meta")
        with open(meta_path) as meta_file:
            raw = meta_file.read()

        metadata = ModelMetaData.model_validate_json(raw, by_name=True)
        return metadata

    def load_metadata_from_filepath(self, path: Path) -> Any:
        pass
