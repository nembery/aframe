from django.http import HttpResponseRedirect


def index(request):
    print "Redirecting to /input_forms"
    return HttpResponseRedirect("/input_forms/")

