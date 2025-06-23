from django.contrib import admin
from django.urls import path
from .views import (ReviewCreateView, ReviewDetalView, ReviewsHome,
                    ReviewDeleteView, ReviewUpdateView,
                    post_search, recommend_multiple_reviews, recommend_multiple_preview, review_preview,
                    load_more_reviews, get_total_count
    )

app_name = 'reviews'

"""
Ниже url маршруты
"""
urlpatterns = [

    path('', ReviewsHome.as_view(), name='reviews_main'),  # Основной адрес
    path('create/', ReviewCreateView.as_view(), name='review_create'),  # url для создания
    path('update/<int:pk>/', ReviewUpdateView.as_view(), name='review_update'),  # url для редактирования
    path('delete/<int:pk>/', ReviewDeleteView.as_view(), name='review_delete'),  # url для удаления
    path('detail/<int:pk>/', ReviewDetalView.as_view(), name='review_detal'),  # url карточка обзора
    path('search', post_search, name='search'),  # url для результатов поиска
    # path('recommend/<int:pk>/', review_share, name='recommend_review'),  # url для отправки 1 обзора
    path('recommend-multiple/', recommend_multiple_reviews, name='recommend_multiple_reviews'),  # url для массовой рассылки
    path('recommend_multiple/preview/', recommend_multiple_preview, name='recommend_multiple_preview'),
    path('review-preview/<int:pk>/', review_preview, name='review_preview'),
    path('api/load-more/', load_more_reviews, name='load_more_reviews'),  # API для прогрессивной загрузки
    path('api/total-count/', get_total_count, name='get_total_count'),  # API для получения количества записей
]
