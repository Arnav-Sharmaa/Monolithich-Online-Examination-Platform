from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from datetime import datetime

# Model for storing questions in the question bank
class Question_DB(models.Model):
    # ForeignKey to link questions to the professor who created them
    professor = models.ForeignKey(User, limit_choices_to={'groups__name': "Professor"}, on_delete=models.CASCADE, null=True)
    qno = models.AutoField(primary_key=True)  # Auto-incrementing question number
    question = models.CharField(max_length=100)  # Question text
    optionA = models.CharField(max_length=100)  # Option A
    optionB = models.CharField(max_length=100)  # Option B
    optionC = models.CharField(max_length=100)  # Option C
    optionD = models.CharField(max_length=100)  # Option D
    answer = models.CharField(max_length=200)  # Correct answer

    def __str__(self):
        return f'Question No.{self.qno}: {self.question} \t\t Options: \nA. {self.optionA} \nB.{self.optionB} \nC.{self.optionC} \nD.{self.optionD} '

# Form for creating or updating questions
class QForm(ModelForm):
    class Meta:
        model = Question_DB
        fields = '__all__'
        exclude = ['qno', 'professor']  # Excluding auto-generated qno and professor


# Model for grouping special students (like in cohorts or classes)
class Special_Students(models.Model):
    professor = models.ForeignKey(User, limit_choices_to={'groups__name': "Professor"}, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=10)  # Category or group name
    students = models.ManyToManyField(User, limit_choices_to={'groups__name': "Student"}, related_name='student_groups')

    def __str__(self):
        return self.category_name

# Form for managing special student groups
class Group_Form(ModelForm):
    class Meta:
        model = Special_Students
        fields = '__all__'
        exclude = ['professor']  # Professor is added automatically


# Model for creating question papers, linking multiple questions together
class Question_Paper(models.Model):
    professor = models.ForeignKey(User, limit_choices_to={'groups__name': "Professor"}, on_delete=models.CASCADE)
    qPaperTitle = models.CharField(max_length=100)  # Title of the question paper
    questions = models.ManyToManyField(Question_DB)  # Many questions can be added to a single paper

    def __str__(self):
        return f'Question Paper Title :- {self.qPaperTitle}'


# Model for creating exams, linking professors, question papers, and special student groups
class Exam_Model(models.Model):
    professor = models.ForeignKey(User, limit_choices_to={'groups__name': "Professor"}, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)  # Exam name
    total_marks = models.IntegerField()  # Total marks for the exam
    duration = models.IntegerField()  # Duration in minutes
    question_paper = models.ForeignKey(Question_Paper, on_delete=models.CASCADE, related_name='exams')  # Linked question paper
    student_group = models.ManyToManyField(Special_Students, related_name='exams')  # Groups of students who will take the exam
    start_time = models.DateTimeField(default=datetime.now())  # Exam start time
    end_time = models.DateTimeField(default=datetime.now())  # Exam end time

    def __str__(self):
        return self.name

# Form for managing exams
class ExamForm(ModelForm):
    class Meta:
        model = Exam_Model
        fields = '__all__'
        exclude = ['professor']  # Professor is filled automatically


# Model for tracking students' answers to individual questions
class Stu_Question(Question_DB):
    professor = None  # Overriding the professor field as not needed here
    student = models.ForeignKey(User, limit_choices_to={'groups__name': "Student"}, on_delete=models.CASCADE, null=True)
    choice = models.CharField(max_length=3, default="E")  # Student's selected answer choice (e.g., A, B, C, D)

    def __str__(self):
        return f'Student Answer - {self.choice} for Question {self.qno}'


# Model for storing student-specific exam data
class StuExam_DB(models.Model):
    student = models.ForeignKey(User, limit_choices_to={'groups__name': "Student"}, on_delete=models.CASCADE, null=True)
    examname = models.CharField(max_length=100)  # Name of the exam
    qpaper = models.ForeignKey(Question_Paper, on_delete=models.CASCADE, null=True)  # Linked question paper
    questions = models.ManyToManyField(Stu_Question)  # Student's answers to each question
    score = models.IntegerField(default=0)  # Score obtained by the student
    completed = models.IntegerField(default=0)  # Marks if the exam is completed (1 for yes, 0 for no)

    def __str__(self):
        return f'Exam for {self.student.username} - {self.examname}'


# Model for storing the results of students for multiple exams
class StuResults_DB(models.Model):
    student = models.ForeignKey(User, limit_choices_to={'groups__name': "Student"}, on_delete=models.CASCADE, null=True)
    exams = models.ManyToManyField(StuExam_DB)  # Exams associated with the student

    def __str__(self):
        return f'Results for {self.student.username}'
