from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^bots/', include('bots.urls')),
    url(r'^discord/', include('discord_connector.urls')),
]
