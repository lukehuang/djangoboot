from django.views.generic import CreateView, UpdateView, DeleteView, View
from django.views.generic.edit import FormMixin, SingleObjectMixin
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.contrib.auth import logout
from django.shortcuts import redirect

from core.views import LoginRequiredMixin
from accounts.models import Group, User


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(request.GET.get('next', 'home:index'))


class GroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    template_name = 'accounts/group_create.html'


class GroupUpdateView(LoginRequiredMixin, UpdateView):
    model = Group
    template_name = 'accounts/group_update.html'


class GroupDeleteView(LoginRequiredMixin, DeleteView):
    model = Group
    template_name = 'accounts/group_delete.html'


class GroupMixin(LoginRequiredMixin, FormMixin, SingleObjectMixin):
    def get_groups_queryset(self):
        user = self.request.user
        return Group.objects.filter(Q(default_users=user) | Q(users=user))

    def get_object(self, queryset=None):
        obj = super(GroupMixin, self).get_object(queryset)
        if obj.group and not self.get_groups_queryset().filter(id=obj.group.id):
            raise PermissionDenied()
        return obj

    def get_form(self):
        form = super(GroupMixin, self).get_form()
        if hasattr(form, 'group'):
            form.group.queryset = self.get_groups_queryset()
        return form
