from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from django.utils.html import escape

from .models import Claim, Annotation, Author

# Register your models here.

class ClaimAdmin(admin.ModelAdmin):
    list_display = ('claim_text', 'claim_handle', 'claim_date')
    ordering = ('-claim_date',)
    fields = ('show_media', 'claim_source', 'claim_handle', 'claim_text', 'claim_type', 'exists', 'claim_date')
    list_filter = ('claim_handle', 'claim_date')

class AuthorAdmin(admin.ModelAdmin):
    ordering = ('first_name',)

class AnnotationAdmin(SummernoteModelAdmin):
    filter_vertical = ('claims',)

    list_display = ('annotation_text_display', 'get_claims', 'author', 'published')
    def annotation_text_display(self, obj):
        from django.utils.html import strip_tags
        stripped = strip_tags(obj.annotation_text)
        return (stripped[:100] + '...') if len(stripped) > 100 else stripped

    annotation_text_display.short_description = 'Annotation'

    def get_claims(self, obj):
        return "\n".join([c.claim_text for c in obj.claims.all().order_by('claim_date')])
    get_claims.short_description = 'Claims'

admin.site.register(Claim, ClaimAdmin)
admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(Author, AuthorAdmin)