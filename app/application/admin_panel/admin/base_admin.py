from app.application.admin_panel.admin.abusive_exp_keys_admin import AbusiveExperienceKeyModelAdmin
from app.application.admin_panel.admin.link_admin import LinkModelAdmin
from app.application.admin_panel.admin.proxy_admin import ProxyModelAdmin
from app.application.admin_panel.admin.result_admin import ResultModelAdmin
from app.application.admin_panel.admin.virus_total_keys_admin import VirusTotalKeyModelAdmin
from sqladmin import Admin


def create_admin(app):
    admin = Admin(
        app,
        app.container.core.db.provided()._engine,  # noqa
        session_maker=app.container.core.db.provided()._async_session,  # noqa
    )
    admin.add_view(LinkModelAdmin)
    admin.add_view(ResultModelAdmin)
    admin.add_view(AbusiveExperienceKeyModelAdmin)
    admin.add_view(VirusTotalKeyModelAdmin)
    admin.add_view(ProxyModelAdmin)

    return admin
