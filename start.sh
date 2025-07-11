docker build -t infinity:v1 -f Dockerfile --build-arg FILENAME=app.py --build-arg PORT=8000 .
az acr login --name infinity.azurecr.io
docker push infinity.azurecr.io/infinity:v1