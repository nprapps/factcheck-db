from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
import json
import subprocess

from .models import Annotation

@receiver(post_save, sender=Annotation)
@receiver(m2m_changed, sender=Annotation.claims.through)
def publish_json(sender, instance, **kwargs):
    with open('annotations.json', 'w') as f:
        annotations = Annotation.objects.filter(published=True)
        payload = []
        for annotation in annotations:
            claims = []
            for claim in annotation.claims.all():
                claim_data = {
                    'text': claim.claim_text,
                    'type': claim.claim_type,
                    'source': claim.claim_source,
                    'date': claim.claim_date.isoformat()
                }

                claims.append(claim_data)

            data = {
                'claims': claims,
                'annotation': annotation.annotation_text,
                'author': '{0} {1}'.format(annotation.author.first_name, annotation.author.last_name),
                'title': annotation.author.author_title,
                'image': annotation.author.author_image,
                'page': annotation.author.author_page
            }
            payload.append(data)
        
        json.dump(payload, f)