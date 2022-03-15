# Django_blog

### Описание проекта:
    Данный проект выполнен в рамках курса "Python - разработчик : бекэнд на django" от Яндекс.Практикум
    и представляет из себя полноценную платформу для блога с авторизацией, персональными лентами, с 
    комментариями и подпиской на авторов. Можно использовать как в качестве самостоятельного ресурса, 
    так и для внедрения в более крупные проекты. 

### Инструкция по развертыванию проекта:
    Клонировать репозиторий и перейти в него в командной строке:
    
        git clone https://github.com/Nikita-Kechaev/django_blog
        cd django_blog
    
    Cоздать и активировать виртуальное окружение:
    
        For Unix: python3 -m venv env
        for Win: python -m venv venv

        For Unix: source env/bin/activate
        for Win: PS: venv/scripts/activate
        OR cmd: /venv/Scripts/activate.bat

        For Unix: python3 -m pip install --upgrade pip
        for Win: python -m pip install --upgrade pip

    Установить зависимости из файла requirements.txt:

        For Unix: pip install -r requirements.txt
        for Win: pip install -r requirements.txt

    Выполнить миграции:

        For Unix: python3 manage.py migrate
        for Win: python manage.py migrate

    Запустить проект:

        For Unix: python3 manage.py runserver
        for Win: python manage.py runserver
        
### Системные требования
    
    Зависимости и необходимые системные требования нах - ся в файле requirements.txt

### Расширение проекта
    Расширение функционала предполагает добавление системы оценок авторов и публикации другими пользователями,
    добавление персональной домашней страницы для авторов публикаций.
    Для возможных расширений проекта написаны тесты с использованием библиотеки django.test:
        Для запуска тестов выполнить команду:
  
            python3 manage.py test
    
    
         

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)
