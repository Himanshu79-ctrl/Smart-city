from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from ..models import Worker
from ..forms import StaffUserForm, WorkerForm
from ..utils.decorators import admin_required
from django.views.decorators.http import require_POST

@login_required
@admin_required
def add_staff(request):

    if request.method == 'POST':
        user_form = StaffUserForm(request.POST, request.FILES)
        worker_form = WorkerForm(request.POST)

        if user_form.is_valid() and worker_form.is_valid():
            user = user_form.save(commit=False)
            user.user_type = 'department_staff'
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            worker = worker_form.save(commit=False)
            worker.user = user
            worker.save()

            return redirect('staff_list')

    else:
        user_form = StaffUserForm()
        worker_form = WorkerForm()

    return render(request, 'accounts/add_staff.html', {
        'user_form': user_form,
        'worker_form': worker_form
    })


@login_required
@admin_required
def staff_list(request):
    staff = Worker.objects.select_related('user', 'department')
    return render(request, 'accounts/staff_list.html', {'staff': staff})


@login_required
@admin_required
def staff_detail(request, id):
    staff = get_object_or_404(Worker, id=id)
    return render(request, 'accounts/staff_detail.html', {'staff': staff})

@never_cache
@login_required
@admin_required
@require_POST
def delete_staff(request, id):
    if not request.user.is_superuser:
        return redirect('unauthorized')

    staff = get_object_or_404(Worker, id=id)
    staff.user.delete()

    return redirect('staff_list')
