from django.urls import path,include
from .views import *

app_name = "pgxpiplineapp"

urlpatterns =[
    path("bam_runner",BamRunnerView.as_view(),name="pipeline-pgx"),
    path("results1/<str:id>",get_results1,name="results1"),
    path("results2/<str:id>",get_results2,name="results2"),
    path("results3/<str:id>",get_results3,name="results3"),
    path("results4/<str:id>",get_results4,name="results4"),
    path("results5/<str:id>",get_results5,name="results5"),
    path("history",get_history,name="history")
]
