from django.urls import path
from django.shortcuts import redirect
from survey.views.api.index import IndexApi
from survey.views.api.survey_form import SurveyFormApi
from survey.views.api.survey_missing_anime import SurveyMissingAnimeApi
from survey.views.api.survey_results import SurveyResultsApi
from survey.views.api.user import UserApi
from survey.views.index import IndexView
from survey.views.form import FormView, MissingAnimeView
from survey.views.notifications import NotificationsView
from survey.views.results import ResultsView, FullResultsView

app_name = 'survey'

def favicon_redirect(request):
    return redirect('/static/favicon/favicon.ico')

# survey_patterns = [
#     path('<int:year>/<int:season>/<pre_or_post>/', FormView.as_view(), name='form'),
#     path('<int:year>/<int:season>/<pre_or_post>/results/', ResultsView.as_view(), name='results'),
#     path('<int:year>/<int:season>/<pre_or_post>/fullresults/', FullResultsView.as_view(), name='fullresults'),
#     path('<int:year>/<int:season>/<pre_or_post>/missinganime/', MissingAnimeView.as_view(), name='missinganime'),
# ]

# api_patterns = [
urlpatterns = [
    path('index/', IndexApi.as_view()),
    path('user/', UserApi.as_view()),
    path('survey/<int:year>/<int:season>/<pre_or_post>/', SurveyFormApi.as_view()),
    path('survey/<int:year>/<int:season>/<pre_or_post>/missinganime/', SurveyMissingAnimeApi.as_view()),
    path('survey/<int:year>/<int:season>/<pre_or_post>/results/', SurveyResultsApi.as_view()),
]

# urlpatterns = [
#     path('', IndexView.as_view(), name='index'),
#     path('api/', include(api_patterns)),
#     path('survey/', include(survey_patterns)),
#     path('notifications/', NotificationsView.as_view(), name='notifications'),
#     path('favicon.ico', favicon_redirect),
# ]
