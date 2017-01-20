import app_config
import json
import os
import subprocess

from django.db.models.signals import post_save, m2m_changed, post_delete
from django.dispatch import receiver
from .models import Annotation

@receiver(post_save)
@receiver(m2m_changed, sender=Annotation.claims.through)
@receiver(post_delete, sender=Annotation)
def publish_json(sender, instance, **kwargs):
    DEPLOYMENT_TARGET = os.environ.get('DEPLOYMENT_TARGET', None)

    if DEPLOYMENT_TARGET == 'production':
        S3_BUCKET = 'apps.npr.org'
    else:
        S3_BUCKET = 'stage-apps.npr.org'

    with open('annotations.json', 'w') as f:
        annotations = Annotation.objects.filter(published=True)
        payload = []
        for annotation in annotations:
            claims = []
            for claim in annotation.claims.all().order_by('claim_date'):
                claim_data = {
                    'text': claim.claim_text,
                    'type': claim.claim_type,
                    'id': claim.twitter_id(),
                    'date': claim.claim_date.isoformat(),
                    'media': claim.show_media
                }

                claims.append(claim_data)

            data = {
                'claims': claims,
                'annotations': [
                    {
                        'annotation': annotation.annotation_text,
                        'author': '{0} {1}'.format(annotation.author.first_name, annotation.author.last_name),
                        'title': annotation.author.author_title,
                        'image': annotation.author.author_image,
                        'page': annotation.author.author_page
                    }
                ]
            }
            payload.append(data)
        
        sorted_annotations = sorted(payload, key=sort_annotations, reverse=True)
        json.dump(sorted_annotations, f)

    subprocess.run(['aws', 's3', 'cp', 'annotations.json', 's3://{0}/{1}/'.format(S3_BUCKET, app_config.PROJECT_FILENAME), '--acl', 'public-read', '--cache-control', 'max-age=30'])


def sort_annotations(block):
    if len(block['claims']) > 0:
        return block['claims'][-1]['date']
    else:
        return '0'