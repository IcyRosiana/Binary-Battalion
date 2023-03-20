from django.shortcuts import render

# Create your views here.
def home(request):
	title = 'Welcome: This is the Home Page'
	form = 'Welcome: This is the Home Page'
	context = {
	"title": title,
	"test": form,
	}
	return render(request, "home.html",context)