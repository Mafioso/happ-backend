from mongoengine import signals

from .models import FileObject

signals.post_delete.connect(FileObject.post_delete, sender=FileObject)
