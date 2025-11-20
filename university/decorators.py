from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('admin_id'):
            messages.error(request, "You must be logged in as an admin.")
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper

def student_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('student_id'):
            messages.error(request, "You must be logged in as a student to access this page.")
            return redirect('student_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def instructor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('instructor_id'):
            messages.error(request, "You must be logged in as an instructor to access this page.")
            return redirect('instructor_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
