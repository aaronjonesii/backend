from rest_framework import viewsets, renderers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


from .serializers import PostSerializer, TagSerializer, CategorySerializer, UserSerializer, NewsletterSerializer
from .models import Tag, Post, Category, NewsletterSubscriber

from django.contrib.auth.forms import AuthenticationForm
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from rest_framework import views, status

from rest_framework import permissions
from django.contrib.auth import logout
from rest_framework_simplejwt.exceptions import TokenError

from requests import get # IP
from rest_framework.decorators import api_view


class NewsletterSubscription(viewsets.ModelViewSet):
    """
    Subscribe email to newsletter.
    """
    serializer_class = NewsletterSerializer
    queryset = NewsletterSubscriber.objects.all().filter(isactive=True)

    def perform_create(self, serializer):
        email = self.request.data['email']
        queryset = NewsletterSubscriber.objects.filter(email=email).filter(isactive=True)
        if queryset.exists():
            raise ValidationError('You are already subscribed!')
        else:
            serializer.save(isactive=True)


class NewsletterUnsubscription(views.APIView):
    def post(self, request):
        ip = get_client_ip(request)
        email = request.data.get('email', None)
        if email is None:
            response = {"error": "Invalid context!"}  # Correct dictionary key was not found
            raise ValidationError(response)
        else:
            existingSubscriber = NewsletterSubscriber.objects.filter(email=email)
            if existingSubscriber.exists():
                existingSubscriber = existingSubscriber.first()
                if existingSubscriber.isactive:
                    existingSubscriber.isactive = False
                    existingSubscriber.save()
                    response = {"success": f"Email unsubscribed!"}  # Successfully unsubscribed email
                else:
                    response = {"success": f"Email not subscribed!"}  # Email was already unsubscribed
            else:
                response = {"error": f"Invalid email!"}  # Email not found in the system
                raise ValidationError(response)
            return Response(response)


class PostViewSet(viewsets.ModelViewSet):
    """
    CRUD endpoint for blogging platform.
    """
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return Post.objects.filter(author=user)

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def byline(self, request, *args, **kwargs):
        post = self.get_object()
        return Response(post.byline)

    @action(detail=True)
    def tags(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = TagSerializer(post.tags, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def related_posts(self, request, *args, **kwargs):
        post = self.get_object()
        related_posts = []
        for tag in post.tags:
            related_posts_from_tag = Post.objects.filter(tag__name=tag)
            for related_post in related_posts_from_tag:
                if post != related_post and related_post not in related_posts:
                    related_posts.append(related_post)
        # print(f'Post: {post} \nRelated posts: {related_posts}')
        serializer = PostSerializer(related_posts, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    """
    CRUD endpoint for tags.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticated,)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD endpoint for tags.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticated,)


class CustomLoginJWTAuthToken(views.APIView):
    """
    API endpoint that takes credentials to return JWT tokens
    """

    def post(self, request):
        form = AuthenticationForm(data=request.data)
        if form.is_valid():
            user = form.get_user()
            login(request, user=form.get_user())

            refresh = RefreshToken.for_user(request.user)
            response = {'token': {
                                'access_token': str(refresh.access_token),
                                'refresh_token': str(refresh),
                            }}
            return Response(response)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomSignUpJWTAuthToken(views.APIView):
    """
    API endpoint to create a new user
    """

    def post(self, request):
        data = request.data
        form = UserSerializer(data=data)
        if form.is_valid():
            new_user = form.save()
            login(request, user=new_user)

            refresh = RefreshToken.for_user(request.user)
            return Response({
                'token': {
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                },
        })
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class LogOutView(views.APIView):
    """
    API endpoint that allows signed in users to Logout
    """
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, *args, **kwargs):
        logout(self.request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomRefreshJWTAuthToken(views.APIView):
    """
    API endpoint that takes a refresh token to return an access token
    """

    def post(self, request):
        import json
        json_data = json.loads(json.dumps(request.data))
        if 'payload' in json_data and 'refresh_token' in json_data['payload']:
            tokens = json_data['payload']
            try:
                refresh = RefreshToken(token=tokens['refresh_token'])
                response = {'token': {
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                }}
            except TokenError:
                return Response({"error": "Invalid token!"}, status=status.HTTP_401_UNAUTHORIZED)
            return Response(response)
        else:
            return Response({"error": "Invalid key!"}, status=status.HTTP_400_BAD_REQUEST)


@api_view()
def weatherView(request):
    ip = get_client_ip(request)
    locationKey = getAccuWeatherLocationKey(ip)
    if locationKey == None:
        return Response({"error": "Invalid locationKey!"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        response = getCurrentConditions(locationKey)
        # print(f'IP: {ip}\nlocationKey: {locationKey}\n Response: {response}')
        return Response(response)


@api_view()
def forecastWeatherView(request):
    ip = get_client_ip(request)
    locationKey = getAccuWeatherLocationKey(ip)
    if locationKey == None:
        return Response({"error": "Invalid locationKey!"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        response = getFiveDayForecast(locationKey)
        return Response(response)


def getAccuWeatherLocationKey(ip=None, postal_code=None):
    ''' Get AccuWeather Location Key from Ip Address '''
    from django.conf import settings
    # API_KEY = settings.ACCUWEATHER_APIKEY
    API_KEY = 'SSnwmKXaoAt1mGH5RDuoyQ3vH0Ey9k36'
    ip = '76.20.137.56'
    url = f'http://dataservice.accuweather.com/locations/v1/cities/ipaddress?q={ip}&apikey={API_KEY}'
    resp = get(url)
    if resp.status_code == 200:
        locationKey = resp.json().get('Key')
        return locationKey
    else:
        return None


def getCurrentConditions(locationKey):
    ''' Returns current conditions data for a specific location.
    Current conditions searches require a location key.
    Please use the Locations API to obtain the location key for your desired location.
    By default, a truncated version of the current conditions data is returned.
    The full object can be obtained by passing "details=true" into the url string. '''
    API_KEY = 'SSnwmKXaoAt1mGH5RDuoyQ3vH0Ey9k36'
    fulldetails = 'true'
    url = f'http://dataservice.accuweather.com/currentconditions/v1/{locationKey}?details={fulldetails}&apikey={API_KEY}'
    try:
        resp = get(url)
        currentConditions = resp.json()[0]
        return currentConditions
    except KeyError:
        return None


def getFiveDayForecast(locationKey):
    ''' Returns an array of daily forecasts for the next 5 days for a specific location.
    Forecast searches require a location key.
    Please use the Locations API to obtain the location key for your desired location.
    By default, a truncated version of the hourly forecast data is returned.
    The full object can be obtained by passing "details=true" into the url string. '''
    API_KEY = 'SSnwmKXaoAt1mGH5RDuoyQ3vH0Ey9k36'
    fulldetails = 'true'
    url = f'http://dataservice.accuweather.com/forecasts/v1/daily/5day/{locationKey}?details={fulldetails}&apikey={API_KEY}'
    resp = get(url)
    fivedayForecast = resp.json()
    return fivedayForecast


@api_view()
def ipView(request):
    ''' IP View '''
    ip = get_client_ip(request)
    response = ipinfo(ip)
    return Response({'content': response})


@api_view()
def searchIP(request, query_ip):
    ''' IP Search View '''
    response = ipinfo(query_ip)
    return Response({'content': response})


def ipinfo(query_ip):
    ''' Get information from IP Address '''
    url = "https://ipinfo.io/"
    resp = get(url + query_ip)
    return resp.json()


def get_client_ip(request):
    ''' Get IP Address '''
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_addr = x_forwarded_for.split(',')[0]
    else:
        ip_addr = request.META.get('REMOTE_ADDR')
    return '8.8.8.8' if ip_addr == '127.0.0.1' else ip_addr
