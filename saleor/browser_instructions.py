from django.template.response import TemplateResponse


def instructions(request, browser=None):
    browser = browser
    if browser:
        return TemplateResponse(request, 'instructions.html', {'browser': browser})
