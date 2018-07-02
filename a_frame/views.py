from django.http import HttpResponseRedirect
from common.lib import aframe_utils


def index(request):
    conf = aframe_utils.load_config()
    print(conf)
    if 'default_screen' in conf and conf['default_screen'] != '':
        print("Redirecting to initial screen")
        return HttpResponseRedirect("/screens/%s" % conf['default_screen'])

    print("Redirecting to /input_forms")
    return HttpResponseRedirect("/input_forms/")

