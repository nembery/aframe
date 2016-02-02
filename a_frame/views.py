from django.http import HttpResponseRedirect


def index(request):
    print "Redirecting to /endpoints"
    return HttpResponseRedirect("/endpoints/")

