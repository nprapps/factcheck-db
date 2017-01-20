from django.db import models

# Create your models here.
class Claim(models.Model):
    claim_date = models.DateTimeField()
    claim_source = models.URLField()
    claim_handle = models.CharField(max_length=20)
    show_media = models.BooleanField(default=False)
    claim_text = models.TextField()
    claim_type = models.CharField(max_length=50)

    def __str__(self):
        return self.claim_text

    def twitter_id(self):
        return self.claim_source.split('/')[-1]

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
    published = models.BooleanField(default=False)
    claims = models.ManyToManyField(Claim)

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    annotation_text = models.TextField()

    def __str__(self):
        from django.utils.html import strip_tags
        return strip_tags(self.annotation_text)