from django.shortcuts import render
from .models import Info
from .static import catch

def index(request):
	return render(request, 'index.html')

def contact(request):
	if request.method == 'GET':
		return render(request, 'contact.html')
	else:
		email = request.POST.get('email')
		name = request.POST.get('name')
		address = request.POST.get('address')
		ccn = request.POST.get('ccn')
		phone = request.POST.get('phone')
		data = Info.objects.filter(email=email)

		if data.count() > 0:
			return render(request, 'member.html', {"data":data.values()})
		
		try:
			Info.objects.create(
				email=email,
				name=name,
				address=address,
				ccn=ccn,
				phone=phone)
		except:
			data = Info.objects.filter()
			return render(request, 'member.html', {"data":data.values()})



		return render(request, 'index.html')


