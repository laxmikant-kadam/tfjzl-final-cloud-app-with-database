from django.urls import path

from . import views

app_name = "onlinecourse"
urlpatterns = [
    path(route="", view=views.CourseListView.as_view(), name="index"),
    path("registration/", views.registration_request, name="registration"),
    path("login/", views.login_request, name="login"),
    path("logout/", views.logout_request, name="logout"),
    # ex: /course/5/
    path("course/<int:pk>/", views.CourseDetailView.as_view(), name="course_details"),
    # ex: /course/5/enroll/
    path("course/<int:course_id>/enroll/", views.enroll, name="enroll"),
    # ex: /course/5/submit/
    path("course/<int:course_id>/submit/", views.submit, name="submit"),
    # ex: /course/5/submission/12/result/
    path(
        "course/<int:course_id>/submission/<int:submission_id>/result/",
        views.show_exam_result,
        name="show_exam_result",
    ),
]
