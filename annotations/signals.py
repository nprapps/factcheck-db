from django.db.models.signals import post_save
from django.dispatch import receiver
import json
import subprocess

from .models import Annotation

@receiver(post_save, sender=Annotation)
def publish_json(sender, instance, **kwargs):
    with open('annotations.json', 'w') as f:
        annotations = Annotation.objects.all()
        payload = []
        for annotation in annotations:
            data = {
                'claim': annotation.claim.claim_text,
                'type': annotation.claim.claim_type,
                'source': annotation.claim.claim_source,
                'annotation': annotation.annotation_text,
                'author': '{0} {1}'.format(annotation.author.first_name, annotation.author.last_name),
                'title': annotation.author.author_title,
                'image': annotation.author.author_image,
                'page': annotation.author.author_page
            }
            payload.append(data)
        
        json.dump(payload, f)