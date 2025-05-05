# Django Ayudamemoria

## Docker + Django + PostgreSQL

```bash
# Configuración inicial
cp .env.example .env
docker-compose up --build
# Si Django no se conecta a PostgreSQL (normal)
docker restart cobra_system
# Dentro del contenedor
docker exec -it cobra_system bash
python ./sistema_cobranza/manage.py migrate
python manage.py createsuperuser

# Resetear estáticos (producción)
docker-compose -f docker-compose.prod.yml exec cobra_system python manage.py collectstatic --no-input --clear
```

## Nuevo Proyecto Django

```bash
# Crear proyecto y app
django-admin startproject mysite
python manage.py startapp polls

# Servidor desarrollo
python manage.py runserver 0:80

# Base de datos
python manage.py migrate                     # Aplicar migraciones iniciales
python manage.py makemigrations polls        # Crear migraciones
python manage.py sqlmigrate polls 0001       # Ver SQL generado
python manage.py migrate                     # Aplicar migraciones

# Admin
python manage.py createsuperuser
```

## Flujo de Trabajo
1. Configurar settings.py (BD, INSTALLED_APPS)
2. Crear modelos en models.py
3. Registrar en admin.py
4. Configurar urls.py (proyecto y app)
5. Crear views.py

## ORM (Consultas)

```python
# Básicas
Model.objects.all()
Model.objects.filter(campo='valor')
Model.objects.get(id=1)

# Crear/Editar
obj = Model(campo='valor')
obj.save()
Model.objects.create(campo='valor')
Model.objects.get(id=1).delete()

# Avanzadas
from django.db.models import Q
Model.objects.filter(Q(campo1='valor1') | Q(campo2='valor2'))
```

## Autenticación

```python
# Decorador para proteger vistas
@login_required

# Token (settings.py)
INSTALLED_APPS = [
    'rest_framework',
    'rest_framework.authtoken',  # Simple
    'knox',                      # Avanzado
]
```

## Enlaces Útiles
- [QuerySet API](https://docs.djangoproject.com/es/3.2/ref/models/querysets/)
- [Autenticación](https://docs.djangoproject.com/en/3.2/topics/auth/default/)
- [Video Tutorial](https://youtube.com/playlist?list=PLEsfXFp6DpzTD1BD1aWNxS2Ep06vIkaeW)
- [Token Simple](https://simpleisbetterthancomplex.com/tutorial/2018/11/22/how-to-implement-token-authentication-using-django-rest-framework.html)
- [Token Knox](https://james1345.github.io/django-rest-knox/)
- [Nginx + Django](https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/#nginx)