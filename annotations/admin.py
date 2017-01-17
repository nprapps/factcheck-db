from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from .models import Claim, Annotation, Author

# Register your models here.

class ClaimAdmin(admin.ModelAdmin):
    list_display = ('claim_text', 'claim_type', 'claim_date')
    ordering = ('-claim_date',)

class AuthorAdmin(admin.ModelAdmin):
    ordering = ('first_name',)

class AnnotationAdmin(SummernoteModelAdmin):
    pass

admin.site.register(Claim, ClaimAdmin)
admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(Author, AuthorAdmin)