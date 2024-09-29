from django.contrib import admin
from .models import *

# Register models for professor-related functionalities
admin.site.register(Question_DB)
admin.site.register(Question_Paper)
admin.site.register(Special_Students)
admin.site.register(Exam_Model)

# Register models for student-related functionalities
admin.site.register(Stu_Question)
admin.site.register(StuExam_DB)
admin.site.register(StuResults_DB)
