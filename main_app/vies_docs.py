from django.shortcuts import render

def api_docs(request):
    return render(request, "docs/api_docs.html")