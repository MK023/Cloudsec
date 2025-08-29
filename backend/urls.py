from django.urls import include, path

urlpatterns = [
    # ... altre route ...
    path("", include("core.urls")),
]
