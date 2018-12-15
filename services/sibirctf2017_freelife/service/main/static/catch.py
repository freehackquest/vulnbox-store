from django.contrib.auth.models import User

try:
	User.objects.create_superuser(
		username='hack',
		password='pass',
		email='')
except:
	pass