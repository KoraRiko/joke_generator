Render : https://dashboard.render.com/web/srv-ctia3i9opnds739q4po0/deploys/dep-cticep5svqrc73ft1j8g

Comands for lockalhost:
  Install dependencies (if needed):   pip install -r requirements.txt
  Apply migrations:                   python manage.py makemigrations
                                      python manage.py migrate
  Start the development server:       python manage.py runserver

  -------------------------
  Docker_hub : korarika/anegen

Comands for Docker:

docker build -t anegen:latest .

docker run -d --name django-anegen-cont -p 8000:8000 anegen

*delete container "django-anegen-cont"*

docker-compose up -d

docker tag anegen korarika/anegen

docker push korarika/anegen

legacy:
Docker_hub : korarika/django-docker

Comands for Docker:

  docker build -t django-docker:latest .
  
  docker run -d --name django-doc-cont -p 8000:8000 django-docker
  
  *delete container*
  
  docker-compose up -d
  
  docker tag django-docker korarika/django-docker 
  
  docker push korarika/django-docker
  
