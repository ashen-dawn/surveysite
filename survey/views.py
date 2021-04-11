from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404 # HttpResponse
from django.db.models import F, Q, Avg
from django.db.models.query import EmptyQuerySet
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.cache import cache
#from django.template import loader
from datetime import datetime
from enum import Enum, auto
import allauth
import logging

from .models import Survey, Anime, AnimeName, Response, AnimeResponse, SurveyAdditionRemoval
from .util import AnimeUtil, SurveyUtil, get_user_info
from .resultview import ResultsGenerator, ResultsType
from .forms import ResponseForm, PreSeasonAnimeResponseForm, PostSeasonAnimeResponseForm


# ======= VIEWS =======
def index(request):
    """Generates the index view, containing a list of current and past surveys."""
    survey_queryset = Survey.objects.order_by('-year', '-season', 'is_preseason')


    for survey in survey_queryset:
        if survey.is_ongoing:
            score_ranking = []
        else:
            def get_score_ranking():
                anime_series_results, _ = ResultsGenerator(survey).get_anime_results_data()
                return sorted(
                    [(anime, anime_data[ResultsType.SCORE]) for anime, anime_data in anime_series_results.items()],
                    key=lambda item: item[1] if item[1] == item[1] else -1,
                    reverse=True,
                )

            if SurveyUtil.is_survey_old(survey):
                score_ranking = cache.get_or_set('survey_score_ranking_%i' % survey.id, get_score_ranking, version=1, timeout=SurveyUtil.get_old_survey_cache_timeout())
            else:
                score_ranking = get_score_ranking()

        
        survey.score_ranking = score_ranking[:3]

    context = {
        'survey_list': survey_queryset,
        'user_info': get_user_info(request.user),
    }

    return render(request, 'survey/index.html', context)



#@user_passes_test(__reddit_check)
@login_required
def form(request, year, season, pre_or_post):
    """Generates the form view, where users can respond to a survey. Requires the user being logged in."""

    # Send the user back to the index if the survey is closed.
    survey = SurveyUtil.get_survey_or_404(year, season, pre_or_post)
    if not survey.is_ongoing:
        messages.error(request, str(survey) + ' is closed!')
        return redirect('survey:index')

    anime_list, anime_series_list, special_anime_list = SurveyUtil.get_survey_anime(survey)
    previous_response = None # TODO: Get previous response when possible
    AnimeResponseForm = PreSeasonAnimeResponseForm if survey.is_preseason else PostSeasonAnimeResponseForm


    # -----
    # The user has submitted a response
    # -----
    if request.method == 'POST':
        responseform = ResponseForm(request.POST, instance=previous_response) if previous_response else ResponseForm(request.POST)
        animeresponseform_list = []

        # Get the anime response forms, bound to already stored anime responses whenever possible
        for anime in anime_list:
            animeresponse_queryset = AnimeResponse.objects.filter(response=previous_response, anime=anime) if previous_response else None
            if animeresponse_queryset and animeresponse_queryset.count() == 1:
                animeresponseform_list.append(AnimeResponseForm(request.POST, prefix=str(anime.id), instance=animeresponse_queryset.first()))
            else:
                animeresponseform_list.append(AnimeResponseForm(request.POST, prefix=str(anime.id)))

        # If all the forms contain valid data, save them
        if responseform.is_valid() and all(map(lambda animeresponseform: animeresponseform.is_valid(), animeresponseform_list)):
            response = Response(
                survey=survey,
                age=responseform.cleaned_data.get('age'),
                gender=responseform.cleaned_data.get('gender'),
            )
            response.save()

            animeresponse_list = []
            for animeresponseform in animeresponseform_list:
                if animeresponseform.cleaned_data:
                    animeresponse_list.append(AnimeResponse(
                        anime=Anime.objects.get(pk=int(animeresponseform.prefix)),
                        score=animeresponseform.cleaned_data.get('score', None),
                        watching=animeresponseform.cleaned_data.get('watching', False),
                        underwatched=animeresponseform.cleaned_data.get('underwatched', False),
                        expectations=animeresponseform.cleaned_data.get('expectations', AnimeResponse.Expectations.__empty__),
                        response=response,
                    ))
            AnimeResponse.objects.bulk_create(animeresponse_list)

            messages.success(request, 'Successfully filled in %s!' % str(survey))
            return redirect('survey:index')

        # If at least one form contains invalid data, re-render the form
        else:
            messages.error(request, 'One or more of your answers are invalid.')
            animeresponseform_dict = {int(form.prefix): form for form in animeresponseform_list}
            return __render_form(request, survey, anime_series_list, special_anime_list, responseform, animeresponseform_dict)


    # -----
    # The user wants to view the form
    # -----
    elif request.method == 'GET':
        responseform = ResponseForm(instance=previous_response) if previous_response else ResponseForm()
        animeresponseform_dict = {}

        # Get the anime response forms, bound to already stored anime responses whenever possible
        # (Saving what anime an AnimeResponseForm belongs to requires AnimeResponse.anime to be editable, so I just store it in the prefix)
        for anime in anime_list:
            animeresponse_queryset = AnimeResponse.objects.filter(response=previous_response, anime=anime) if previous_response else None
            if animeresponse_queryset and animeresponse_queryset.count() == 1:
                animeresponseform_dict[anime.id] = AnimeResponseForm(prefix=str(anime.id), instance=animeresponse_queryset.first())
            else:
                animeresponseform_dict[anime.id] = AnimeResponseForm(prefix=str(anime.id))

        # Render the form
        return __render_form(request, survey, anime_series_list, special_anime_list, responseform, animeresponseform_dict)



def __render_form(request, survey, anime_series_list, special_anime_list, responseform, animeresponseform_dict):
    """Renders a survey form using the provided data."""
    def modify(anime):
        # Get anime names
        names = anime.animename_set.all()
        japanese_name = names.filter(anime_name_type=AnimeName.AnimeNameType.JAPANESE_NAME, official=True).first()
        anime.japanese_name = japanese_name if japanese_name else names.filter(anime_name_type=AnimeName.AnimeNameType.JAPANESE_NAME, official=False).first()
        english_name  = names.filter(anime_name_type=AnimeName.AnimeNameType.ENGLISH_NAME , official=True).first()
        anime.english_name  = english_name  if english_name  else names.filter(anime_name_type=AnimeName.AnimeNameType.ENGLISH_NAME , official=False).first()
        short_name    = names.filter(anime_name_type=AnimeName.AnimeNameType.SHORT_NAME   , official=True).first()
        anime.short_name    = short_name    if short_name    else names.filter(anime_name_type=AnimeName.AnimeNameType.SHORT_NAME   , official=False).first()

        # Get whether the anime is still ongoing or not
        anime.is_ongoing = survey.year != anime.start_year or survey.season != anime.start_season

        # Get a response form for the anime
        anime.animeresponseform = animeresponseform_dict[anime.id]

        return anime

    anime_series_list = map(modify, anime_series_list)
    special_anime_list = map(modify, special_anime_list)

    context = {
        'survey': survey,
        'anime_series_list': anime_series_list,
        'special_anime_list': special_anime_list,
        'user_info': get_user_info(request.user),
        'responseform': responseform,
    }
    return render(request, 'survey/form.html', context)



# ======= HELPER METHODS =======
def __try_get_response(request, item, conversion, value_if_none=None):
    """Tries to get the specified value of an item from the POST request.

    Parameters
    ----------
    request : HttpRequest
        The request sent by the user. Must be a POST request.
    item : str
        The item (key) you want to get the value of.
    conversion : lambda
        Converts the item's value (if it exists).
    value_if_none : any, optional
        Value that gets returned if the item or value doesn't exist or is empty, by default None.

    Returns
    -------
    any
        The value of the item.
    """

    if item not in request.POST.keys() or request.POST.get(item, '') == '':
        return value_if_none
    else:
        return conversion(request.POST.get(item, None))

# Forgot why I stopped using this
def __reddit_check(user):
    """Returns True if the user is authenticated via Reddit."""
    if not user.is_authenticated: return False

    reddit_accounts = user.socialaccount_set.filter(provider='reddit')
    return len(reddit_accounts) > 0
