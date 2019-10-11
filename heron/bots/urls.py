from bots import bot_api_views
from bots import conversation_api_views
from bots import scrape_api_views
from django.conf.urls import url

urlpatterns = [
    url(r'^get_bot/(?P<username>[a-zA-Z_]+)/$', bot_api_views.get_bot),
    url(r'^get_all_bots/', bot_api_views.get_all_bots),
    url(r'^create_top_bots/(?P<limit>[0-9]+)/$', bot_api_views.create_top_bots),
    url(r'^clear_bot_tweets/(?P<username>[a-zA-Z_]+)', bot_api_views.clear_bot_tweets),
    url(r'^create_post/([0-9]+)/$', bot_api_views.create_post),
]

urlpatterns += [
    url(r'^scrape_bot/(?P<username>[a-zA-Z0-9]+)/$', scrape_api_views.scrape_bot),
    url(r'^scrape_all_bots/$', scrape_api_views.scrape_all_bots),
]
urlpatterns += [
    url(r'^get_emotion_bots/', bot_api_views.list_all_emotion_bots),
    url(r'^get_replies_for_tweet/(?P<username>[a-zA-Z]+)/(?P<tweet_id>[0-9]+)/$', bot_api_views.get_replies_for_tweet),
    url(r'^get_tweets_over_threshold_and_analyze_text_understanding/(?P<username>[a-zA-Z]+)/(?P<threshold>[0-9]+)/(?P<response_number>[0-9]+)/(?P<scrape_mode>[a-zA-Z_]+)/$',
        bot_api_views.get_tweets_over_threshold_and_analyze_text_understanding),
    url(r'^update_emotion_bots/$', bot_api_views.update_emotion_bot),
]
urlpatterns += [url(r'^get_conversation/(?P<bot1_username>[a-zA-Z0-9_]+)/(?P<bot2_username>[a-zA-Z0-9_]+)/$',
                    conversation_api_views.get_conversation),
                url(r'^update_conversation/(?P<bot1_username>[a-zA-Z0-9_]+)/(?P<bot2_username>[a-zA-Z0-9_]+)/(?P<post_number>[0-9]+)/$',
                    conversation_api_views.update_conversation),
                url(r'^clear_conversation/(?P<bot1_username>[a-zA-Z_]+)/(?P<bot2_username>[a-zA-Z_]+)/$',
                    conversation_api_views.clear_conversation),
                url(r'^clear_all_conversations/(?P<bot_id>[0-9]+)/$',
                    conversation_api_views.clear_all_conversations),
                url(r'^get_group_conversation/$',
                    conversation_api_views.get_group_conversation),
                url(r'^update_group_conversation/$',
                    conversation_api_views.update_group_conversation),
                ]
