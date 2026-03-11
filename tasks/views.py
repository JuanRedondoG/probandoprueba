from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
import requests

def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {'form': UserCreationForm})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('dashboard')
            except IntegrityError:
                return render(request, 'signup.html', {"form": UserCreationForm, "error": 'El usuario ya existe'})
        return render(request, 'signup.html', {"form": UserCreationForm, "error": 'Las contraseñas no coinciden'})

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {'form': AuthenticationForm})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {'form': AuthenticationForm, 'error': 'Usuario o contraseña incorrectos'})
        else:
            login(request, user)
            return redirect('dashboard')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def opcion(request, num):
    titulo = {
        1: "Datos CESFAM del paciente",
        2: "Rut definitivo / Validar 3 tipos de RUT",
        3: "Profesionales preferidos",
        4: "Cambiar profesionales bloqueados",
        5: "Consultar hora reservada",
        6: "Detalle de hora médica",
        7: "Solicitar hora",
        8: "Solicitar grabación",
        9: "¿Problemas con la app?"
    }.get(num, f"Opción {num}")

    contexto = {
        'num': num,
        'titulo': titulo,
        'contenido': 'Aquí aparecerá la información detallada según la opción seleccionada.'
    }

    # Opción 2 → Validador de 3 tipos de RUT
    if num == 2:
        return redirect('validar_rut')

    return render(request, 'opcion.html', contexto)

@login_required
def validar_rut(request):
    resultados = None
    if request.method == 'POST':
        rut1 = request.POST.get('rut1', '').strip()
        rut2 = request.POST.get('rut2', '').strip()
        rut3 = request.POST.get('rut3', '').strip()
        ruts = [rut1, rut2, rut3]
        resultados = []

        for rut in ruts:
            if rut:
                try:
                    # Validación local + API pública
                    response = requests.get(f"https://boostr.cl/api/validador-rut/{rut}", timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        resultados.append({
                            'rut': rut,
                            'valido': data.get('valido', False),
                            'mensaje': data.get('mensaje', 'RUT procesado'),
                            'tipo': 'Natural' if 'natural' in str(data).lower() else 'Empresa' if 'empresa' in str(data).lower() else 'Provisional'
                        })
                    else:
                        resultados.append({'rut': rut, 'valido': False, 'mensaje': 'Error al consultar', 'tipo': 'Desconocido'})
                except:
                    resultados.append({'rut': rut, 'valido': False, 'mensaje': 'Sin conexión a la API', 'tipo': 'Desconocido'})

    return render(request, 'validar_rut.html', {'resultados': resultados})

def signout(request):
    logout(request)
    return redirect('home')