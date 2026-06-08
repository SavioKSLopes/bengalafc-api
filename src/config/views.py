from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

def hello_world(request):
    return render(request, 'pages/hello-world.html')

def pag2(request):
    return render(request, 'pages/pag2.html')

def signup_view(request):
    errors = []
    next_url = request.GET.get('next', '')
    first_name = ''
    last_name = ''
    email = ''

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        if not first_name or not last_name or not email or not password:
            errors.append("Todos os campos são obrigatórios.")
        elif len(password) < 6:
            errors.append("A senha precisa ter pelo menos 6 caracteres.")
        else:
            try:
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                
                login_url = '/accounts/login/'
                if next_url:
                    login_url += f'?next={next_url}'
                return redirect(login_url)
            except IntegrityError:
                errors.append("Este e-mail já está cadastrado.")
            except Exception as e:
                errors.append(f"Erro ao cadastrar: {str(e)}")

    return render(request, 'registration/signup.html', {
        'errors': errors,
        'next_url': next_url,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
    })