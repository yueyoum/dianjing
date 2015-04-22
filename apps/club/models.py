from django.db import models

class Club(models.Model):
    char_id = models.IntegerField(db_index=True)
    char_name = models.CharField(max_length=32)
    server_id = models.IntegerField()

    name = models.CharField(max_length=32)
    flag = models.IntegerField()
    level = models.IntegerField(default=1)
    renown = models.IntegerField(default=0)
    vip = models.IntegerField(default=0)
    exp = models.IntegerField(default=0)
    gold = models.IntegerField(default=0)
    sycee = models.IntegerField(default=0)


    class Meta:
        db_table = 'club'
        unique_together = (
            ('name', 'server_id')
        )
