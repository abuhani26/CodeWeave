import os
import mimetypes
from django.http import HttpResponse, Http404, FileResponse
from django.conf import settings

def serve_media_with_range(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if not os.path.exists(file_path) or os.path.isdir(file_path):
        raise Http404("Media file not found")

    file_size = os.path.getsize(file_path)
    content_type, _ = mimetypes.guess_type(file_path)
    content_type = content_type or 'application/octet-stream'

    range_header = request.META.get('HTTP_RANGE', '').strip()
    if not range_header or not range_header.startswith('bytes='):
        response = FileResponse(open(file_path, 'rb'), content_type=content_type)
        response['Accept-Ranges'] = 'bytes'
        response['Content-Length'] = str(file_size)
        return response

    try:
        range_spec = range_header.split('bytes=')[1]
        parts = range_spec.split('-')
        start = int(parts[0]) if parts[0] else 0
        end = int(parts[1]) if parts[1] else file_size - 1
    except Exception:
        start = 0
        end = file_size - 1

    if start >= file_size:
        return HttpResponse(status=416)

    end = min(end, file_size - 1)
    length = end - start + 1

    with open(file_path, 'rb') as f:
        f.seek(start)
        data = f.read(length)

    response = HttpResponse(data, status=206, content_type=content_type)
    response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
    response['Accept-Ranges'] = 'bytes'
    response['Content-Length'] = str(length)
    return response
