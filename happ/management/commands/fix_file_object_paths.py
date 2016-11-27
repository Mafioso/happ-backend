import os
import json
import ntpath

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from progressbar import ProgressBar, SimpleProgress

from happ.models import FileObject


class Command(BaseCommand):
    help = 'Rename file objects path to meet requirements of folder structure'

    def path_leaf(self, path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def handle(self, *args, **options):
        pbar = ProgressBar(widgets=[SimpleProgress()], maxval=FileObject.objects.count()).start()
        for idx, f in enumerate(FileObject.objects.all()):
            path = f.path
            if 'event' in path or 'events' in path:
                path = os.path.join(settings.NGINX_UPLOAD_ROOT, self.path_leaf(path))
            elif 'interests' in path:
                path = os.path.join(settings.NGINX_MISC_ROOT, self.path_leaf(path))
            f.path = path
            f.save()
            pbar.update(idx + 1)
        pbar.finish()
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully fixed {} paths'.format(FileObject.objects.count())
            )
        )
