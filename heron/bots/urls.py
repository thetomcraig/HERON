from django.conf.urls import url
from bots import api_views

urlpatterns = [
    url(r'^list_all_bots/', api_views.list_all_bots),
    url(r'^scrape_bot/([0-9]+)/$', api_views.scrape_bot),
    url(r'^get_bot_info/([0-9]+)/$', api_views.get_bot_info),
    url(r'^create_post/([0-9]+)/$', api_views.create_post),
    url(r'^get_conversation/(?P<bot1_id>[0-9]+)/(?P<bot2_id>[0-9]+)/$', api_views.get_conversation),
    url(r'^update_conversation/(?P<bot1_id>[0-9]+)/(?P<bot2_id>[0-9]+)/$', api_views.update_conversation),
    url(r'^clear_conversation/(?P<bot1_id>[0-9]+)/(?P<bot2_id>[0-9+])/$', api_views.clear_conversation),
    url(r'^clear_all_conversations/(?P<bot_id>[0-9]+)/$', api_views.clear_all_conversations),
]
