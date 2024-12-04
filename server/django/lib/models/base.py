from .mixins import TimeAuditModel


class BaseModel(TimeAuditModel):
    class Meta:
        abstract = True

    def __str__(self):
        return str(self.id)
