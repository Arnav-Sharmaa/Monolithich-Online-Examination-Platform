from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User ,Group
from django.utils import timezone
from django import forms
from exam.models import *
from django.contrib.auth.forms import UserCreationForm





#code for sign up 
class SignUpForm(UserCreationForm):
    group = forms.ChoiceField(choices=[('Professor', 'Professor'), ('Student', 'Student')], required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'group']

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Get selected group and assign it to the user
            group_name = form.cleaned_data.get('group')
            group = Group.objects.get(name=group_name)
            user.groups.add(group)

            # Automatically log in the user after registration
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

                # Redirect based on group
                if group_name == 'Professor':
                    return redirect('index_prof')
                else:
                    return redirect('index_stu')

            return redirect('index')  # Redirect to some page after sign-up
    else:
        form = SignUpForm()

    return render(request, 'main/signup.html', {'form': form})

##end

    

# Create your views here.
def index(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser or user.is_staff:
                return redirect('/admin')

            if user.groups.filter(name='Professor').exists():
                return redirect('index_prof')

            return redirect('index_stu')

        return render(request, 'main/login.html', {'wrong_cred_message': 'Error'})

    return render(request, 'main/login.html')
    

def index_prof(request):
    prof = request.user
    return render(request, 'prof/index.html', {'prof': prof })


def index_stu(request):
    student = request.user

    studentGroup = Special_Students.objects.filter(students=student)
    examsList = []
    if studentGroup.exists():
        for student_ in studentGroup:
            stud_exams = Exam_Model.objects.filter(student_group=student_)
            if stud_exams.exists():
                if stud_exams.count() > 1:
                    for stud_exam in stud_exams:
                        examsList.append(stud_exam)
                else:
                    examsList.append(Exam_Model.objects.get(
                        student_group=student_))

    if examsList:
        for exam in examsList:
            currentExamList = StuExam_DB.objects.filter(
                examname=exam.name, student=student)

            if not currentExamList.exists():  # If no exam are there in then add exams
                tempExam = StuExam_DB(student=student, examname=exam.name,
                                        qpaper=exam.question_paper, score=0, completed=0)
                tempExam.save()
                exam_question_paper = exam.question_paper
                questions_in_paper = exam_question_paper.questions.all()
                
                for ques in questions_in_paper:
                    # add all the questions from the prof to student database
                    studentQuestion = Stu_Question(question=ques.question, optionA=ques.optionA, optionB=ques.optionB,
                                                    optionC=ques.optionC, optionD=ques.optionD,
                                                    answer=ques.answer, student=student)
                    studentQuestion.save()
                    tempExam.questions.add(studentQuestion)

    return render(request, 'student/index.html', {
        'stud': student
    })
def logoutUser(request):
    logout(request)
    return render(request, 'main/logout.html', {'logout_message': 'Logged out Successfully'})


def view_exams(request):
    prof = request.user

    new_Form = ExamForm()
    new_Form.fields["student_group"].queryset = Special_Students.objects.filter(
        professor=prof)
    new_Form.fields["question_paper"].queryset = Question_Paper.objects.filter(
        professor=prof)

    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.professor = prof
            exam.save()
            form.save_m2m()
            return redirect('view_exams')

    exams = Exam_Model.objects.filter(professor=prof)

    return render(request, 'prof/exam/view_exams.html', {
        'exams': exams, 'examform': new_Form, 'prof': prof,
    })


def view_exam(request, exam_id):
    prof = request.user
    exam = Exam_Model.objects.get(professor=prof, pk=exam_id)
    return render(request, 'prof/exam/view_exam.html', {
        'exam': exam, 'prof': prof, 'student_group': exam.student_group.all()
    })


def edit_exam(request, exam_id):
    prof = request.user
    exam = Exam_Model.objects.filter(professor=prof, pk=exam_id).first()

    new_Form = ExamForm(instance=exam)
    new_Form.fields["student_group"].queryset = Special_Students.objects.filter(professor=prof)
    new_Form.fields["question_paper"].queryset = Question_Paper.objects.filter(professor=prof)

    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            return redirect('view_exams')

    return render(request, 'prof/exam/edit_exam.html', {
        'form': new_Form, 'exam': exam, 'prof': prof
    })


def delete_exam(request, exam_id):
    prof = request.user
    exam = Exam_Model.objects.get(professor=prof, pk=exam_id)
    exam.delete()
    return redirect('view_exams')


def create_student_group(request):
    prof = request.user

    if request.method == "POST":
        form = Group_Form(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.professor = prof
            group.save()
            form.save_m2m()

            return redirect('view_groups')

    return render(request, 'prof/group/addview_groups.html', {
        'special_students_db': Special_Students.objects.filter(professor=prof), 'prof': prof, 'groupForm': Group_Form()
    })


def view_specific_group(request, group_id):
    prof = request.user
    group = Special_Students.objects.get(professor=prof, pk=group_id)

    return render(request, 'prof/group/view_specific_group.html', {
        'group': group, 'prof': prof, 'group_students': group.students.all()
    })


def view_student_in_group(request, group_id):
    prof = request.user
    group = Special_Students.objects.get(professor=prof, pk=group_id)

    if request.method == 'POST':
        student_username = request.POST['username']
        student = User.objects.get(username=student_username)
        group.students.add(student)

    return render(request, 'prof/group/view_special_stud.html', {
        'students': group.students.all(), 'group': group, 'prof': prof
    })


def edit_group(request, group_id):
    prof = request.user
    group = Special_Students.objects.get(professor=prof, pk=group_id)
    group_form = Group_Form(instance=group)

    if request.method == "POST":
        form = Group_Form(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('view_groups')

    return render(request, 'prof/group/edit_group.html', {
        'prof': prof, 'group': group, 'group_form': group_form
    })


def delete_group(request, group_id):
    prof = request.user
    Special_Students.objects.filter(professor=prof, pk=group_id).delete()
    return redirect('view_groups')


def add_question(request):
    prof = request.user

    if request.method == 'POST':
        form = QForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.professor = prof
            form.save()
            return redirect('view_all_ques')

    return render(request, 'prof/question/question.html', {
        'question_db': Question_DB.objects.filter(professor=prof), 'form': QForm(), 'prof': prof
    })


def view_all_ques(request):
    prof = request.user

    if request.method == 'POST':
        Q_No = int(request.POST['qno'])
        sum_ = 1 + Question_DB.objects.filter(professor=prof).count()

        for i in range(Q_No + 1, sum_):
            ques = Question_DB.objects.filter(
                professor=prof, qno=int(i)).first()
            ques.qno -= 1
            ques.save()

        sum_ -= 1

        Question_DB.objects.filter(professor=prof, qno=Q_No).delete()

    return render(request, 'prof/question/view_all_questions.html', {
        'question_db': Question_DB.objects.filter(professor=prof), 'prof': prof
    })


def edit_question(request, ques_qno):
    prof = request.user
    ques = Question_DB.objects.get(professor=prof, qno=ques_qno)
    form = QForm(instance=ques)

    if request.method == "POST":
        form = QForm(request.POST, instance=ques)
        if form.is_valid():
            form.save()
            return redirect('view_all_ques')

    return render(request, 'prof/question/edit_question.html', {
        'i': Question_DB.objects.filter(professor=prof, qno=ques_qno).first(), 'form': form, 'prof': prof
    })


def make_paper(request):
    prof = request.user

    if request.method == 'POST' and not request.POST.get('presence', False):
        add_question_in_paper(request)

    elif request.method == 'POST' and request.POST.get('presence', False):
        title = request.POST['title']
        Question_Paper.objects.filter(professor=prof, qPaperTitle=title).first().delete()

    return render(request, 'prof/question_paper/qpaper.html', {
        'qpaper_db': Question_Paper.objects.filter(professor=prof), 'prof': prof
    })


def add_question_in_paper(request):
    prof = request.user

    if request.method == 'POST' and request.POST.get('qpaper', False):
        paper_title = request.POST['qpaper']
        question_paper = Question_Paper(professor=prof, qPaperTitle=paper_title)
        question_paper.save()

        left_ques = []
        curr_paper_questions = question_paper.questions.all()
        for ques in Question_DB.objects.filter(professor=prof):
            if ques not in curr_paper_questions:
                left_ques.append(ques)

        return render(request, 'prof/question_paper/addquestopaper.html', {
            'qpaper': question_paper,
            'question_list': left_ques, 'prof': prof
        })

    elif request.method == 'POST' and request.POST.get('title', False):
        addques = request.POST['title']
        ques_ = Question_DB.objects.filter(professor=prof, qno=addques).first()
        title = request.POST['papertitle']
        ques_paper = Question_Paper.objects.filter(professor=prof, qPaperTitle=title).first()
        ques_paper.questions.add(ques_)
        ques_paper.save()

        left_ques = []
        curr_paper_questions = ques_paper.questions.all()
        for ques in Question_DB.objects.filter(professor=prof):
            if ques not in curr_paper_questions:
                left_ques.append(ques)

        return render(request, 'prof/question_paper/addquestopaper.html', {
            'qpaper': ques_paper, 'question_list': left_ques, 'prof': prof
        })

    return render(request, 'prof/question_paper/addquestopaper.html')


def view_paper(request):
    prof = request.user

    if request.method == 'POST':
        papertitle = request.POST['title']
        ques_paper = Question_Paper.objects.get(professor=prof, qPaperTitle=papertitle)

        return render(request, 'prof/question_paper/viewpaper.html', {
            'qpaper': ques_paper, 'question_list': ques_paper.questions.all(), 'prof': prof
        })


def edit_paper(request):
    prof = request.user

    if request.method == 'POST' and request.POST.get('title', False):
        papertitle = request.POST['title']
        ques_paper = Question_Paper.objects.filter(professor=prof, qPaperTitle=papertitle).first()

        left_ques = []
        curr_paper_questions = ques_paper.questions.all()
        for ques in Question_DB.objects.filter(professor=prof):
            if ques not in curr_paper_questions:
                left_ques.append(ques)

        return render(request, 'prof/question_paper/editpaper.html', {
            'ques_left': left_ques, 'qpaper': ques_paper, 'question_list': ques_paper.questions.all(), 'prof': prof
        })

    elif request.method == 'POST' and request.POST.get('remove', False):
        papertitle = request.POST['paper']
        no = request.POST['question']
        ques_paper = Question_Paper.objects.filter(professor=prof, qPaperTitle=papertitle).first()
        ques = Question_DB.objects.filter(professor=prof, qno=no).first()
        ques_paper.questions.remove(ques)
        ques_paper.save()

        left_ques = []
        curr_paper_questions = ques_paper.questions.all()
        for ques in Question_DB.objects.filter(professor=prof):
            if ques not in curr_paper_questions:
                left_ques.append(ques)

        return render(request, 'prof/question_paper/editpaper.html', {
            'ques_left': left_ques, 'qpaper': ques_paper, 'question_list': ques_paper.questions.all(), 'prof': prof
        })

    elif request.method == 'POST' and request.POST.get('qnumber', False) != False:
        qno = request.POST['qnumber']
        ptitle = request.POST['titlepaper']
        ques_paper = Question_Paper.objects.filter(
            professor=prof, qPaperTitle=ptitle).first()
        a = Question_DB.objects.filter(professor=prof, qno=qno).first()
        ques_paper.questions.add(a)
        ques_paper.save()

        left_ques = []
        curr_paper_questions = ques_paper.questions.all()
        for ques in Question_DB.objects.filter(professor=prof):
            if ques not in curr_paper_questions:
                left_ques.append(ques)

        return render(request, 'prof/question_paper/editpaper.html', {
            'ques_left': left_ques, 'qpaper': ques_paper, 'question_list': ques_paper.questions.all(), 'prof': prof
        })


def view_specific_paper(request, paper_id):
    prof = request.user

    paper = Question_Paper.objects.get(professor=prof, pk=paper_id)
    return render(request, 'prof/question_paper/viewpaper.html', {
        'qpaper': paper, 'question_list': paper.questions.all(), 'prof': prof
    })


def view_students(request):
    prof = request.user
    return render(request, 'prof/student/view_students.html', {
        'students': User.objects.filter(groups__name='Student'), 'prof': prof
    })


def exams(request):
    student = request.user

    studentGroup = Special_Students.objects.filter(students=student)
    studentExamsList = StuExam_DB.objects.filter(student=student)

    if request.method == 'POST' and not request.POST.get('papertitle', False):
        paper = request.POST['paper']
        stuExam = StuExam_DB.objects.get(examname=paper, student=student)
        qPaper = stuExam.qpaper
        examMain = Exam_Model.objects.get(name=paper)

        # TIME COMPARISON
        exam_start_time = examMain.start_time
        curr_time = timezone.now()

        if curr_time < exam_start_time:
            return redirect('exams')

        stuExam.questions.all().delete()

        qPaperQuestionsList = qPaper.questions.all()
        for ques in qPaperQuestionsList:
            student_question = Stu_Question(question=ques.question, optionA=ques.optionA, optionB=ques.optionB,
                                            optionC=ques.optionC, optionD=ques.optionD,
                                            answer=ques.answer, student=student)
            student_question.save()
            stuExam.questions.add(student_question)
            stuExam.save()

        stuExam.completed = 1
        stuExam.save()
        mins = examMain.duration
        secs = 0

        return render(request, 'student/paper/viewpaper.html', {
            'qpaper': qPaper, 'question_list': stuExam.questions.all(), 'student': student, 'exam': paper, 'min': mins,
            'sec': secs
        })

    elif request.method == 'POST' and request.POST.get('papertitle', False):
        paper = request.POST['paper']
        title = request.POST['papertitle']
        stuExam = StuExam_DB.objects.get(examname=paper, student=student)
        qPaper = stuExam.qpaper

        examQuestionsList = stuExam.questions.all()
        examScore = 0
        for ques in examQuestionsList:
            ans = request.POST.get(ques.question, False)
            if not ans:
                ans = "E"
            ques.choice = ans
            ques.save()
            if ans == ques.answer:
                examScore = examScore + 1

        stuExam.score = examScore
        stuExam.save()

        return render(request, 'student/result/result.html', {
            'Title': title, 'Score': examScore, 'student': student
        })

    return render(request, 'student/exam/viewexam.html', {
        'student': student, 'paper': studentExamsList
    })


def results(request):
    student = request.user

    studentGroup = Special_Students.objects.filter(students=student)
    studentExamList = StuExam_DB.objects.filter(student=student, completed=1)

    if request.method == 'POST':
        paper = request.POST['paper']
        viewExam = StuExam_DB.objects.get(examname=paper, student=student)
        return render(request, 'student/result/individualresult.html', {
            'exam': viewExam, 'student': student, 'quesn': viewExam.questions.all()
        })

    return render(request, 'student/result/results.html', {
        'student': student, 'paper': studentExamList
    })

