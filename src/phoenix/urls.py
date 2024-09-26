"""
URL configuration for phoenix project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/accounts/login/')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('loan/', include('loan.urls')),
    path('client/', include('client.urls')),
    path('reports/', include('reports.urls')),
    path('bank/', include('bank.urls')),
    path('main', include('main.urls')),
    path('savings/', include('savings.urls')),
    path('income/', include('income.urls')),
    path('expense/', include('expenses.urls')),
    path('asset/', include('asset.urls')),
    path('liability/', include('liability.urls')),
]
