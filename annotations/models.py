from django.db import models

# Create your models here.
class Claim(models.Model):
    claim_date = models.DateTimeField()
    claim_source = models.URLField()
    claim_handle = models.CharField(max_length=20)
    show_media = models.BooleanField(default=False)
    claim_text = models.TextField()
    claim_type = models.CharField(max_length=50)
    exists = models.BooleanField(default=True)

    def __str__(self):
        base = '@{0}: {1}'.format(self.claim_handle, self.claim_text)

        if self.exists:
            return base
        else:
            return '[DELETED] {0}'.format(base)

    def twitter_id(self):
        return self.claim_source.split('/')[-1]

class Author(models.Model):
    initials = models.CharField(max_length=3)
    first_name = models.CharField(max_length=50)    
    last_name = models.CharField(max_length=50)
    author_title = models.CharField(max_length=100)
    author_image = models.URLField(null=True, blank=True)
    author_page = models.URLField(null=True, blank=True)

    def __str__(self):
        return '{0} {1}'.format(self.first_name, self.last_name)

class Annotation(models.Model):
    published = models.BooleanField(default=False)
    claims = models.ManyToManyField(Claim)

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    annotation_text = models.TextField()

    def __str__(self):
        from django.utils.html import strip_tags
        stripped = strip_tags(self.annotation_text)

        return (stripped[:75] + '...') if len(stripped) > 75 else stripped