from discord_connector import views
from django.conf.urls import url

urlpatterns = [
    url(r'message_received', views.message_received),
    url(r'reply_query', views.reply_query),
]
