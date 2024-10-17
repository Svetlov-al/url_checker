from app.adapters.orm.virus_total import VirusTotalModel
from sqladmin import ModelView


class VirusTotalModelAdmin(ModelView, model=VirusTotalModel):
    column_list = (
        VirusTotalModel.id,
        VirusTotalModel.result,
        VirusTotalModel.link,
        VirusTotalModel.created_at,
        VirusTotalModel.updated_at,
    )
