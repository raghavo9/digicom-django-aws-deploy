FROM python:3.8
ENV PYTHONUNBUFFERED=1
WORKDIR /app

#COPY requirements.txt requirements.txt
#because we are copying everything except myenv , kept myenv in .dockerignore
COPY . .

RUN pip install --upgrade pip 

RUN pip install -r /app/requirements.txt 

#CMD ["python","manage.py","runserver","0.0.0.0:8000"]
CMD ["gunicorn","DigiCom.wsgi:application","--bind", "0.0.0.0:8000"]



