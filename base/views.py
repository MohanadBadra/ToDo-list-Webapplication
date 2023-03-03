from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
# enter -> LOGIN_URL = "login" into settings.py
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin   # using it as paramater to restricted classes(pages)
# the mixin ^ will redirect to the deafult login page from the settings.py/LOGIN_URL
from .models import Task


# Create your views here.
class CustomLoginView(LoginView):   # it the same if you signed from the admin panel '/admin'
    fields = '__all__' # in html -> {{form.as_p}}
    template_name = 'base/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('tasks')
    
class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')
    
    def form_valid(self, form):
        user = form.save()
        if user != None:
            login(self.request, user)
        return super().form_valid(form)
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)
    
class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = "tasks" # to call the object via the html..
    # The deafult template will be "task_list"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        
        search_input = self.request.GET.get("search-area") or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(title__startswith=search_input)
        context['count'] = context['tasks'].filter(complete=False).count()
        context['search_input'] = search_input
        return context
    
class TaskDetail(DetailView):
    model = Task
    context_object_name = "task"
    template_name = "base/task.html"    # The deafult template won't be "model_detail" longer

class TaskCreate(CreateView):
    model = Task
    fields = ['title', 'description', 'complete']  # fields=['title', 'description',...]
    success_url = reverse_lazy('tasks')  # 'tasks' from .urls.py
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)
    
class TaskUpdate(UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

class TaskDelete(DeleteView):
    model = Task
    context_object_name = "task"
    success_url = reverse_lazy('tasks')