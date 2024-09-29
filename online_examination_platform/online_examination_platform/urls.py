from django.contrib import admin
from django.urls import path
from exam import views  # Importing views from exam app

urlpatterns = [
    # Admin and index routes
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('logout/', views.logoutUser, name='logoutUser'),

    # Professor Exam Management
    path('prof/exams/', views.view_exams, name='view_exams'),
    path('prof/exams/<int:exam_id>/', views.view_exam, name='view_exam'),
    path('prof/exams/<int:exam_id>/edit/', views.edit_exam, name='edit_exam'),
    path('prof/exams/<int:exam_id>/delete/', views.delete_exam, name='delete_exam'),

    # Professor Student Group Management
    path('prof/viewgroups/', views.create_student_group, name='view_groups'),
    path('prof/viewgroups/<int:group_id>/', views.view_specific_group, name='view_specific_group'),
    path('prof/viewgroups/<int:group_id>/students/', views.view_student_in_group, name='view_students_in_group'),
    path('prof/viewgroups/<int:group_id>/edit/', views.edit_group, name='edit_group'),
    path('prof/viewgroups/<int:group_id>/delete/', views.delete_group, name='delete_group'),

    # Professor Question Management
    path('prof/question/', views.add_question, name='add_question'),
    path('prof/question/view_all_ques/', views.view_all_ques, name='view_all_ques'),
    path('prof/question/view_all_ques/edit_question/<int:ques_qno>/', views.edit_question, name='edit_question'),

    # Professor Question Paper Management
    path('prof/questionpaper/', views.make_paper, name='make_paper'),
    path('prof/questionpaper/addquestion/', views.add_question_in_paper, name="add_question_in_paper"),
    path('prof/questionpaper/viewpaper/', views.view_paper, name='view_paper'),
    path('prof/questionpaper/editpaper/', views.edit_paper, name='edit_paper'),
    path('prof/questionpaper/viewpaper/<int:paper_id>/', views.view_specific_paper, name='view_specific_paper'),

    # Professor Students View
    path('prof/students/', views.view_students, name='view_students'),

    # Student Exam and Result Views
    path('student/exams/', views.exams, name='exams'),
    path('student/results/', views.results, name='results'),
]
