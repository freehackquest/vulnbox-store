from django.db import models

class Info(models.Model):
	name = models.CharField(max_length=60)
	email = models.CharField(max_length=60)
	address = models.CharField(max_length=100)
	phone = models.CharField(max_length=60)
	ccn = models.CharField(max_length=60)

	def __str__(self):
		return self.email