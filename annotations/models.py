from django.db import models

# Create your models here.
class Claim(models.Model):
    claim_text = models.TextField()
    claim_type = models.CharField(max_length=50)
    claim_date = models.DateTimeField()
    claim_source = models.URLField()

    def __str__(self):
        return self.claim_text

class Author(models.Model):
    initials = models.CharField(max_length=3)
    first_name = models.CharField(max_length=50)    
    last_name = models.CharField(max_length=50)
    author_title = models.CharField(max_length=100)
    author_image = models.URLField()
    author_page = models.URLField()

    def __str__(self):
        return '{0} {1}'.format(self.first_name, self.last_name)

class Annotation(models.Model):
    claims = models.ManyToManyField(Claim)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    annotation_text = models.TextField()
    published = models.BooleanField(default=False)

    def __str__(self):
        from django.utils.html import strip_tags
        return strip_tags(self.annotation_text)