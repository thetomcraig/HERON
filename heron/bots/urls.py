from bots import api_views
from django.conf.urls import url

urlpatterns = [
    url(r'^list_all_bots/', api_views.list_all_bots),
    url(r'^get_emotion_bots/', api_views.list_all_emotion_bots),
    url(r'^scrape_bot/(?P<username>[a-zA-Z]+)/$', api_views.scrape_bot),
    url(r'^get_replies_for_tweet/(?P<username>[a-zA-Z]+)/(?P<tweet_id>[0-9]+)/$', api_views.get_replies_for_tweet),
    url(r'^get_tweets_over_threshold_and_analyze_text_understanding/(?P<username>[a-zA-Z]+)/(?P<threshold>[0-9]+)/(?P<response_number>[0-9]+)/(?P<scrape_mode>[a-zA-Z_]+)/$',
        api_views.get_tweets_over_threshold_and_analyze_text_understanding),
    url(r'^get_bot_info/(?P<username>[a-zA-Z_]+)/$', api_views.get_bot_info),
    url(r'^clear_bot_tweets/(?P<username>[a-zA-Z_]+)', api_views.clear_bot_tweets),
    url(r'^create_post/([0-9]+)/$', api_views.create_post),
    url(r'^get_conversation/(?P<bot1_username>[a-zA-Z_]+)/(?P<bot2_username>[a-zA-Z_]+)/$', api_views.get_conversation),
    url(r'^clear_conversation/(?P<bot1_username>[a-zA-Z_]+)/(?P<bot2_username>[a-zA-Z_]+)/$', api_views.clear_conversation),
    url(r'^clear_all_conversations/(?P<bot_id>[0-9]+)/$', api_views.clear_all_conversations),
    url(r'^update_conversation/$', api_views.update_conversation),
    url(r'^update_emotion_bots/$', api_views.update_emotion_bot),
]
