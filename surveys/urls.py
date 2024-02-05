from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("survey/<int:survey_id>/", views.survey_detail, name="survey_detail"),
    path("survey/<int:survey_id>/submit/", views.submit_survey, name="submit_survey"),
    path("survey/<int:survey_id>/result/", views.survey_result, name="survey_result"),
]
