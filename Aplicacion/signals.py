from django.db import connection
from django.db.backends.signals import connection_created
from django.dispatch import receiver

@receiver(connection_created)
def set_search_path(sender, connection, **kwargs):
    cursor = connection.cursor()
    cursor.execute("SET search_path TO datamart, public")
