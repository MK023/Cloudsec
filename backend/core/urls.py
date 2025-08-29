"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from core import views
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.api_urls")),  # Include the API URLs from core app
    path("healthz/", views.healthz, name="healthz"),  # Health check endpoint
]

# Le rotte per le API delle crypto e delle news sono gestite in core/api_urls.py,
# che ora include sia CryptoCurrencyViewSet che NewsViewSet registrati sul router DRF.
# Non è necessaria alcuna modifica qui: la struttura delle URL è corretta e pronta per supportare entrambe le risorse.
