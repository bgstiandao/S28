from django.shortcuts import render
from web.forms.issues import IssuesModelForm

def issues(request, project_id):
    form = IssuesModelForm(request)
    return render(request,'issues.html',{'form':form})