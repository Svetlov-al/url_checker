from app.adapters.orm.base_link import LinkModel
from sqladmin import ModelView


class LinkModelAdmin(ModelView, model=LinkModel):
    column_list = (
        LinkModel.id,
        LinkModel.url,
        LinkModel.created_at,
        LinkModel.updated_at,
    )

    is_async = True

    name_plural = "Базовые Ссылки"
