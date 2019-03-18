from django.contrib import admin
from .models import Question, Choice


class ChoiceInLine(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Basic fields', {'fields': ['question_text']}),
        ("Date information", {'fields': ['pub_date'], 'classes': ['collapse']})
    ]
    inlines = [ChoiceInLine]


admin.site.register(Question, QuestionAdmin)
