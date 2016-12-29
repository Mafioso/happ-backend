import os
import json
import shutil
import ntpath

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from progressbar import ProgressBar, SimpleProgress

from happ.models import FileObject


class Command(BaseCommand):
    help = 'Changes file objects path scheme and move files'

    def add_arguments(self, parser):
        parser.add_argument('--mv', type=bool, nargs='?')

    def path_leaf(self, path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def handle(self, *args, **options):
        pbar = ProgressBar(widgets=[SimpleProgress()], maxval=FileObject.objects.count()).start()
        for idx, f in enumerate(FileObject.objects.all()):
            path = f.path
            filename = self.path_leaf(path)
            if 'media' in path:
                dest_folder = os.path.join(settings.NGINX_UPLOAD_ROOT, str(f.entity.id))
            if 'misc' in path:
                dest_folder = os.path.join(settings.NGINX_MISC_ROOT, str(f.entity.id))
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)
            if os.path.exists(path):
                shutil.move(path, os.path.join(dest_folder, filename))
            f.path = os.path.join(dest_folder, filename)
            f.save()
            pbar.update(idx + 1)
        pbar.finish()
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully fixed {} paths'.format(FileObject.objects.count())
            )
        )
