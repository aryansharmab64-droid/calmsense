from django.conf import settings


def project_meta(request):
    return {"PROJECT": settings.PROJECT_META}