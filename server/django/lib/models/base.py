from django.db import models


class BaseModel(models.Model):
    class Meta:
        abstract = True

    def __str__(self):
        return str(self.id)
