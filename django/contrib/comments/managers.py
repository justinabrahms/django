from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode

class CommentQuerySet(models.query.QuerySet):
    def in_moderation(self):
        """
        QuerySet for all comments currently in the moderation queue.
        """
        return self.filter(is_public=False, is_removed=False)

    def not_in_moderation(self):
        """
        QuerySet for all comments currently not in the moderation queue, i.e.,
        all the comments that are publicly viewable.
        """
        # The is_public and is_removed fields are implementation details of the
        # built-in comment model's spam filtering system, so they might not
        # be present on a custom comment model subclass. If they exist, we
        # should filter on them.
        field_names = [f.name for f in self.model._meta.fields]
        if 'is_public' in field_names:
            qs = self.filter(is_public=True)
        if getattr(settings, 'COMMENTS_HIDE_REMOVED', True) and 'is_removed' in field_names:
            qs = qs.filter(is_removed=False)
        return qs

    def for_model(self, model):
        """
        QuerySet for all comments for a particular model (either an instance or
        a class).
        """
        ct = ContentType.objects.get_for_model(model)
        qs = self.filter(content_type=ct)
        if isinstance(model, models.Model):
            qs = qs.filter(object_pk=force_unicode(model._get_pk_val()))
        return qs

class CommentManager(models.Manager):

    def get_query_set(self):
        return CommentQuerySet(self.model, using=self._db)

    def in_moderation(self):
        """
        QuerySet for all comments currently in the moderation queue.
        """
        return self.get_query_set().in_moderation()

    def not_in_moderation(self):
        """
        QuerySet for all comments currently not in the moderation queue, i.e.,
        all the comments that are publicly viewable.
        """
        return self.get_query_set().not_in_moderation()

    def for_model(self, model):
        """
        QuerySet for all comments for a particular model (either an instance or
        a class).
        """
        return self.get_query_set().for_model(model)
