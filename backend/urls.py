from django.urls import path, include

urlpatterns = [
    # ... altre route ...
    path('', include('core.urls')),
]