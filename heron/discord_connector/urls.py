from discord_connector import views
from django.conf.urls import url

urlpatterns = [
    url(r"bot_online", views.bot_online),
    url(r"get_message", views.get_message),
]
