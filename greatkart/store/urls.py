from django.urls import path
#from django.conf import settings
#from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    # Products by Category Slug URL 
    path('category/<slug:category_slug>/', views.store, name='products_by_category'),
    # Product Detail URL
    path('category/<slug:category_slug>/<slug:product_slug>', views.product_detail, name='product_detail'),
    # Search URL
    path('search/', views.search, name='search'),
] 
