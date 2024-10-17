from app.adapters.orm.abusive_experience import AbusiveExperienceModel
from sqladmin import ModelView


class AbusiveExperienceModelAdmin(ModelView, model=AbusiveExperienceModel):
    column_list = (
        AbusiveExperienceModel.id,
        AbusiveExperienceModel.result,
        AbusiveExperienceModel.link,
        AbusiveExperienceModel.created_at,
        AbusiveExperienceModel.updated_at,
    )
