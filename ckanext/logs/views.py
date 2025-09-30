from __future__ import annotations

from flask import Blueprint

import ckan.plugins.toolkit as tk

from ckanext.tables.shared import GenericTableView

bp = Blueprint("logs", __name__, url_prefix="/ckan-admin/logs")


def before_request() -> None:
    try:
        tk.check_access("sysadmin", {"user": tk.current_user.name})
    except tk.NotAuthorized:
        tk.abort(403, tk._("Need to be system administrator to administer"))


bp.before_request(before_request)

bp.add_url_rule(
    "/dashboard", view_func=GenericTableView.as_view("dashboard", table="logs")
)
