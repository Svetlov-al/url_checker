from app.adapters.orm.credentials.abusive_experience_keys import AbusiveExperienceKeyModel
from sqladmin import ModelView


class AbusiveExperienceKeyModelAdmin(ModelView, model=AbusiveExperienceKeyModel):
    column_list = (
        AbusiveExperienceKeyModel.id,
        AbusiveExperienceKeyModel.api_key,
        AbusiveExperienceKeyModel.is_valid,
        AbusiveExperienceKeyModel.created_at,
        AbusiveExperienceKeyModel.updated_at,
        AbusiveExperienceKeyModel.daily_limit,
        AbusiveExperienceKeyModel.used_limit,
    )

    is_async = True

    name_plural = "Ключи AbusiveExperience"
