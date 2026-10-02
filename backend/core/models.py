"""
PKL CMS — Core Base Models
Semua model mewarisi dari BaseModel untuk konsistensi ID UUID dan timestamps.
"""

import uuid
from django.db import models


class BaseModel(models.Model):
    """
    Abstract base model yang diwarisi semua model domain.
    - UUID sebagai primary key (non-sequential, aman untuk public API)
    - created_at/updated_at otomatis dikelola
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.__class__.__name__}({self.id})"
