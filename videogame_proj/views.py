from django.shortcuts import render
from django.http import HttpResponse

"""
Error Pages
"""
def handler404(request, exception):
    return render(request, "error_pages/404.html")

def handler500(request):
    return render(request, "error_pages/500.html")

"""
Sitemap
"""
def sitemap(request):
    return render(request, "xml/sitemap.xml", content_type="text/xml")

"""
Robots.txt
"""
def robotsTxt(request):
    return render(request, "txt/robots.txt", content_type="text/plain")
