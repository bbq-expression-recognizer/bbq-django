from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.core.servers.basehttp import FileWrapper

import os
import mimetypes
import configs

from models import ImageFile

from PIL import Image
import redis

redis_server = redis.StrictRedis(host='localhost', port=6379, db=2, decode_responses=True)

def handle_uploaded_file(f, path):
    destination = open(path, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()

def remove_by_object(file):
    real_path = file.real_path

    file.delete()
    if real_path is not None:
        try:
            os.remove(real_path)
        except:
            pass
    if real_path is not None:
        try:
            os.remove(real_path + "_normalized.png")
        except:
            pass


def remove(request):
    if 'id' not in request.GET:
        return HttpResponseRedirect(reverse('eqnsolver.views.list'))
    fileid = int(request.GET['id'])

    files = ImageFile.objects.filter(id=fileid)
    if len(files) < 1:
        return HttpResponseRedirect(reverse('eqnsolver.views.list'))
    remove_by_object(files[0])
    return HttpResponseRedirect(reverse('eqnsolver.views.list'))

def list(request):
    # Handle file upload
    if request.method == 'POST':
        successcount = 0
        totalcount = len(request.FILES.getlist('file'))
        for f in request.FILES.getlist('file'):
            try:
                if f.size > 20*1024*1024:
                    return HttpResponseRedirect(reverse('eqnsolver.views.list'))

                newfile = ImageFile()
                newfile.original_name = f.name
                newfile.save()

                saved_path = os.path.join(unicode(configs.BASE_FILE_PATH), unicode(newfile.id))
                saved_path = os.path.realpath(saved_path)
                handle_uploaded_file(f, saved_path)

                newfile.real_path = saved_path
                newfile.save()

                # notify to redis
                redis_server.rpush(u"image", unicode(newfile.id) + u"," + unicode(saved_path))
                redis_server.publish(u"request", u"image")
                result_key, result_text = redis_server.blpop(u"result" + unicode(newfile.id))

                # some kind of error occurred
                if result_text is None or len(result_text) == 0:
                    remove_by_object(newfile)
                    continue

                newfile.parsed = result_text
                newfile.save()
                successcount = successcount + 1
            except:
                continue

        files = ImageFile.objects.all()
        # Redirect to the file list after POST
        if successcount == 0:
            msg_class = 'danger'
        elif successcount < totalcount:
            msg_class = 'warning'
        else:
            msg_class = 'success'
        return render_to_response(
            'l.html',
            {'files': files, 'message': 'Processed {} files out of {} files!'.format(successcount, totalcount), 'messageclass': msg_class},
            context_instance=RequestContext(request)
        )


    # Load files for the list page
    files = ImageFile.objects.all()

    # Render list page
    return render_to_response(
        'l.html',
        {'files': files},
        context_instance=RequestContext(request)
    )

def image(request):
    if 'id' not in request.GET:
        return HttpResponseRedirect(reverse('eqnsolver.views.list'))
    fileid = int(request.GET['id'])

    files = ImageFile.objects.filter(id=fileid)
    if len(files) < 1:
        return HttpResponseRedirect(reverse('eqnsolver.views.list'))
    file = files[0]

    real_path = file.real_path
    if real_path is None:
        return HttpResponseRedirect(reverse('eqnsolver.views.list'))


    response = HttpResponse(FileWrapper(open(real_path, 'rb')),
            content_type=mimetypes.guess_type(real_path)[0])
    response['Content-Length'] = os.path.getsize(real_path)
    response['Content-Disposition'] = "attachment; filename=%s" % file.original_name
    return response

def image_norm(request):
    if 'id' not in request.GET:
        return HttpResponseRedirect(reverse('eqnsolver.views.list'))
    fileid = int(request.GET['id'])

    files = ImageFile.objects.filter(id=fileid)
    if len(files) < 1:
        return HttpResponseRedirect(reverse('eqnsolver.views.list'))
    file = files[0]

    real_path = file.real_path
    if real_path is None:
        return HttpResponseRedirect(reverse('eqnsolver.views.list'))

    real_path = real_path + "_normalized.png"

    response = HttpResponse(FileWrapper(open(real_path, 'rb')),
            content_type=mimetypes.guess_type(real_path)[0])
    response['Content-Length'] = os.path.getsize(real_path)
    response['Content-Disposition'] = "attachment; filename=%s" % file.original_name
    return response











