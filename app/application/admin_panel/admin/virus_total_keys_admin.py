from app.adapters.orm.credentials.virus_total_keys import VirusTotalKeyModel
from sqladmin import ModelView


class VirusTotalKeyModelAdmin(ModelView, model=VirusTotalKeyModel):
    column_list = (
        VirusTotalKeyModel.id,
        VirusTotalKeyModel.api_key,
        VirusTotalKeyModel.is_valid,
        VirusTotalKeyModel.created_at,
        VirusTotalKeyModel.updated_at,
    )

    is_async = True

    name_plural = "Ключи VirusTotal "
