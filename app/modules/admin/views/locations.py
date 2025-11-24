
from sqladmin import ModelView

from app.modules.locations.models import Loaction


class locationAdmin(ModelView, model=Loaction):
    name = "Location"
    name_plural = "Locations"
    column_list = [Loaction.id, Loaction.user_id, Loaction.latitude, Loaction.longitude]
    form_columns = [Loaction.user_id, Loaction.latitude, Loaction.longitude]