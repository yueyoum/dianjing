from django.db import models

class Character(models.Model):
    account_id = models.IntegerField()
    server_id = models.IntegerField()
    name = models.CharField(max_length=32, db_index=True)
    create_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'char_'
        unique_together = (
            ('account_id', 'server_id'),
            ('server_id', 'name'),
        )
