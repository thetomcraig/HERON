from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader

from integrations.models.twitter import TwitterPerson, TwitterPost

from integrations.forms import PoolForm
from integrations.helpers.utils import (
    clear_set,
)

from integrations.helpers.twitter_bot_utils import (
    clear_twitter_conversation,
    clear_all_twitter_conversations,
    scrape_twitter_person,
    add_to_twitter_conversation,
    apply_markov_chains_twitter,
    scrape_top_twitter_people,
    update_top_twitter_people,
    get_or_create_conversation,
    get_person_attributes,
)


def twitter_home(request):
    """
    The top twitter profiles, that link to particular users
    """
    if(request.GET.get('go_back_to_home')):
        return HttpResponseRedirect(reverse('home'))

    if(request.GET.get('scrape_top_twitter_people')):
        scrape_top_twitter_people()
        return HttpResponseRedirect('twitter_home/')

    if(request.GET.get('update_top_twitter_people')):
        update_top_twitter_people()
        return HttpResponseRedirect('twitter_home/')

    twitter_people = TwitterPerson.objects.all()
    template = loader.get_template('integrations/twitter_home.html')
    context = {'twitter_people': twitter_people}
    return HttpResponse(template.render(context, request))


def twitter_person_detail(request, person_username):
    if request.method == 'POST':
        form = PoolForm(request.POST)
        if 'go_to_conversation' in request.POST.keys():
            form.is_valid()
            for key in request.POST.keys():
                if key.startswith('twitter_people__'):
                    partner_username = key.replace('twitter_people__', '')
                    return HttpResponseRedirect(reverse('twitter_conversation',
                                                args=(person_username, partner_username)))

    author = None
    all_people = TwitterPerson.objects.all()
    for person in all_people:
        if person.username.strip() == person_username.strip():
            author = person

    attrs = get_person_attributes(person_username)

    all_people_json = {x.username: x.real_name for x in all_people}
    pool_json = {x.username: x.real_name for x in author.pool.all()}
    pool_form = PoolForm(initial={'twitter_people': all_people_json})

    sentences = []
    markov_sentences = []
    person_type = ''

    # Grab data from author if twitter person
    if isinstance(author, TwitterPerson):
        person_type = str(TwitterPerson)
        sentences = TwitterPost.objects.filter(author=author)

        markov_sentences = author.twitterpostmarkov_set.all().order_by('-randomness')

    sentences_to_render = markov_sentences
    # If you are already on the page, these things
    # will happen when you click buttons

    if(request.GET.get('go_back_to_list')):
        return HttpResponseRedirect(reverse('twitter_home'))

    if(request.GET.get('scrape')):
        scrape_twitter_person(author)
        return HttpResponseRedirect('/integrations/twitter_person_detail/' + person_username)

    if(request.GET.get('clear_all_conversations')):
        clear_all_twitter_conversations(person_username)
        return HttpResponseRedirect('/integrations/twitter_person_detail/' + person_username)

    if(request.GET.get('show_original')):
        sentences_to_render = sentences

    if(request.GET.get('show_markov')):
        sentences_to_render = markov_sentences

    if(request.GET.get('generate_post')):
        apply_markov_chains_twitter(author)
        return HttpResponseRedirect('/integrations/twitter_person_detail/' + person_username)

    if(request.GET.get('clear_posts')):
        clear_set(author.twitterpost_set.all())
        clear_set(author.twitterpostcache_set.all())
        clear_set(author.twitterpostmarkov_set.all())
        return HttpResponseRedirect('/integrations/twitter_person_detail/' + person_username)

    if(request.GET.get('show_pool')):
        pool_form = PoolForm(initial={'twitter_people': pool_json})

    if(request.GET.get('show_all')):
        pool_form = PoolForm(initial={'twitter_people': all_people_json})

    if(request.GET.get('add_selected_to_pool')):
        pass

    template = loader.get_template('integrations/twitter_person_detail.html')
    context = RequestContext(request, {
        'attrs': attrs,
        'pool_form': pool_form,
        'person': author,
        'person_type': person_type,
        'sentences': sentences_to_render,
        'len_sentences': len(sentences),
        'len_markov_sentences': len(markov_sentences),
    })

    return HttpResponse(template.render(context))


def twitter_conversation(request, person_username, partner_username):
    if(request.GET.get('go_back_to_list')):
        return HttpResponseRedirect('/integrations/twitter_home')

    if(request.GET.get('new_post')):
        add_to_twitter_conversation(person_username, partner_username)
        return HttpResponseRedirect('/integrations/twitter_conversation/%s/%s/' % (person_username, partner_username))

    if(request.GET.get('clear_conversation')):
        clear_twitter_conversation(person_username, partner_username)
        return HttpResponseRedirect('/integrations/twitter_conversation/%s/%s/' % (person_username, partner_username))

    template = loader.get_template('integrations/twitter_conversation.html')
    conversation = get_or_create_conversation(partner_username, person_username)
    conversation_posts = conversation.twitterconversationpost_set.all()
    sentences = [x.post for x in conversation_posts]

    context = RequestContext(request, {
        'clear_text': 'clear_conversation',
        'clear_text_human': 'Clear Conversation',
        'request': request,
        'sentences': sentences,
        'person_username': person_username,
        'partner_username': partner_username,
    })
    return HttpResponse(template.render(context, request))
