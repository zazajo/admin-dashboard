from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def create_admin_view(request):
    """Temporary view - DELETE AFTER USE!"""
    User = get_user_model()
    
    if User.objects.filter(username='admin').exists():
        return JsonResponse({
            'status': 'error',
            'message': 'Admin already exists!'
        })
    
    try:
        user = User.objects.create_superuser(
            username='admin',
            email='josephedward201@gmail.com',
            password='eddiejoe',
            first_name='Joseph',
            last_name='Edward',
            role='ADMIN'
        )
        return JsonResponse({
            'status': 'success',
            'message': 'Admin user created!',
            'username': 'admin',
            'password': 'eddiejoe',
            'warning': 'DELETE THIS ENDPOINT NOW!'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })