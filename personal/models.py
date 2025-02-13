from django.db import models

class Contact(models.Model):
    name                    = models.CharField(max_length=200)
    email                   = models.EmailField()
    subject                 = models.TextField()
    message                 = models.CharField(max_length=1000)

    def __str__(self):
        return self.name
