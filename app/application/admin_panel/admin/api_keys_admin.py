from app.adapters.orm.credentials.api_keys import APIKeyModel
from sqladmin import ModelView


class APIKeyModelAdmin(ModelView, model=APIKeyModel):
    column_list = (
        APIKeyModel.id,
        APIKeyModel.api_key,
        APIKeyModel.source,
        APIKeyModel.is_valid,
        APIKeyModel.created_at,
        APIKeyModel.updated_at,
        APIKeyModel.daily_limit,
        APIKeyModel.used_limit,
        APIKeyModel.proxies,
    )

    is_async = True

    name_plural = "Ключи доступа к API"
