Render : https://dashboard.render.com/web/srv-ctia3i9opnds739q4po0/deploys/dep-cticep5svqrc73ft1j8g

Docker_hub : korarika/django-docker

Comands for Docker:

  docker build -t django-docker:latest .
  
  docker run -d --name django-doc-cont -p 8000:8000 django-docker
  
  *delete container*
  
  docker-compose up -d
  
  docker tag django-docker korarika/django-docker 
  
  docker push korarika/django-docker
  
