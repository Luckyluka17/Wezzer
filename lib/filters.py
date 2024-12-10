from flask import Blueprint

filters = Blueprint("filters", __name__)

@filters.app_template_filter("get_index")
def get_index(lst, value):
    return lst.index(value) if value in lst else -1