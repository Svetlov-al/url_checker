from app.application.admin_panel.admin.abusive_exp_admin import AbusiveExperienceModelAdmin
from app.application.admin_panel.admin.link_admin import LinkModelAdmin
from app.application.admin_panel.admin.virus_total_admin import VirusTotalModelAdmin
from sqladmin import Admin


def create_admin(app):
    admin = Admin(
        app,
        app.container.core.db.provided()._engine,  # noqa
        session_maker=app.container.core.db.provided()._async_session,  # noqa
    )
    admin.add_view(LinkModelAdmin)
    admin.add_view(AbusiveExperienceModelAdmin)
    admin.add_view(VirusTotalModelAdmin)

    return admin
