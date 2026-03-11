
from django.db import models

class PostgresEnumField(models.CharField):
    def __init__(self, *args, enum_name=None, **kwargs):
        if not enum_name:
            raise ValueError("enum_name is required")
        self.enum_name = enum_name
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        return self.enum_name

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["enum_name"] = self.enum_name
        return name, path, args, kwargs
