from allauth.socialaccount.providers import registry as auth_provider_registry
from dataclasses import dataclass, field
from typing import Optional
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.generic import View
from survey.util.data import DataBase, json_encoder_factory


class UserApi(View):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        jsonEncoder = json_encoder_factory()

        if not request.user or not request.user.is_authenticated:
            auth_provider = auth_provider_registry.by_id('reddit', request)
            auth_url = auth_provider.get_login_url(request)
            return JsonResponse(AnonymousUserData(
                authentication_url=auth_url,
            ), encoder=jsonEncoder, safe=False)

        reddit_account_queryset = self.request.user.socialaccount_set.filter(provider='reddit')
        profile_picture_url = reddit_account_queryset[0].extra_data['icon_img'] if reddit_account_queryset else None
            
        return JsonResponse(AuthenticatedUserData(
            username=request.user.first_name if request.user.first_name else request.user.username,
            profile_picture_url=profile_picture_url,
            is_staff=request.user.is_staff,
        ), encoder=jsonEncoder, safe=False)


@dataclass
class UserData(DataBase):
    authenticated: bool

@dataclass
class AnonymousUserData(UserData):
    authenticated: bool = field(default=False, init=False)
    authentication_url: str

@dataclass
class AuthenticatedUserData(UserData):
    authenticated: bool = field(default=True, init=False)
    is_staff: bool
    username: str
    profile_picture_url: str