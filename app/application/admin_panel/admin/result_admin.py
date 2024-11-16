from app.adapters.orm.result import ResultModel
from sqladmin import ModelView


class ResultModelAdmin(ModelView, model=ResultModel):
    column_list = (
        ResultModel.id,
        ResultModel.virus_total,
        ResultModel.abusive_experience,
        ResultModel.link,
        ResultModel.created_at,
        ResultModel.updated_at,
        ResultModel.complete_date,
    )

    is_async = True

    name_plural = "Результаты обработки"
