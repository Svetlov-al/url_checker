from app.application.admin_panel.admin.api_keys_admin import APIKeyModelAdmin
from app.application.admin_panel.admin.link_admin import LinkModelAdmin
from app.application.admin_panel.admin.proxy_admin import ProxyModelAdmin
from app.application.admin_panel.admin.result_admin import ResultModelAdmin
from sqladmin import Admin


def create_admin(app):
    admin = Admin(
        app,
        app.container.core.db.provided()._engine,  # noqa
        session_maker=app.container.core.db.provided()._async_session,  # noqa
    )
    admin.add_view(LinkModelAdmin)
    admin.add_view(ResultModelAdmin)
    admin.add_view(APIKeyModelAdmin)
    admin.add_view(ProxyModelAdmin)

    return admin
