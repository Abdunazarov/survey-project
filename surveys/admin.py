from django.contrib import admin
from .models import Survey, Question, Answer, Respondent, Response

admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Respondent)
admin.site.register(Response)
