import datetime
from microblog import models

from django.template import RequestContext
from django.shortcuts import render_to_response

def post_detail(request, year, month, day, slug):
    postcontent = models.PostContent.objects.get(
        slug = slug, 
        post__date__year = int(year),
        post__date__month = int(month),
        post__date__day = int(day)
    )
    return render_to_response(
        'microblog/post_detail.html',
        {
            'post': postcontent.post,
            'content': postcontent
        },
        context_instance = RequestContext(request)
    )
