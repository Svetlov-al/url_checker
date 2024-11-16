from app.adapters.orm.proxy import ProxyModel
from sqladmin import ModelView


class ProxyModelAdmin(ModelView, model=ProxyModel):
    column_list = (
        ProxyModel.id,
        ProxyModel.username,
        ProxyModel.password,
        ProxyModel.is_active,
        ProxyModel.created_at,
        ProxyModel.updated_at,
        ProxyModel.api_keys,
    )

    is_async = True

    name_plural = "Прокси"
