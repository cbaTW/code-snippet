# flask
from flask import Blueprint

# views inside cve_formatter folder
from .views.cve_formatter import cve_formatter

cve_formatter_bp = Blueprint("cve_formatter",
                         __name__,
                         static_folder="static",
                         static_url_path="/static",
                         template_folder="templates",
                         url_prefix="/cve_formatter")

cve_formatter_bp.add_url_rule("/cve_formatter", view_func=cve_formatter, methods=["POST"])
