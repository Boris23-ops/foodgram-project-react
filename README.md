# Foodgram
![Workflow](https://github.com/Boris23-ops/foodgram-project-react/actions/workflows/main.yml/badge.svg)
_
## api_Foodgram
Пример запущенного сервиса: 
[foo0dgram.ddns.net](https://foo0dgram.ddns.net)
Документация по адресу:(https://foo0dgram.ddns.net/api/docs/)

### Описание проекта
Проект API и готового фронтенда системы публикации кулинарных рецептов.
Проект создан для всех гурманов, любителей вкусной еды, любителей делится своими кулинарными навыками и для тех кто просто ищет интересный рецепт. Этот проект для всех и каждого, вы можете зарегистрировать на нём собрать свою собственную категорию избранных блюд или следить за публикациями понравившихся авторов.
Еда не только даёт нам энергию, но и может объединять людей.

### Стэк

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB) ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white) ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=blue) ![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)  ![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white) ![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white) ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)   ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)


___
___
# Описание функционала для авторизованных пользователей: 
 
1. Главная страница доступна для просмотра. 
2. Страница другого пользователя доступна для просмотра. 
3. Страница отдельного рецепта доступна для просмотра. 
4. Страница "Мои подписки": 
    - Можно подписаться и отписаться на странице рецепта. 
    - Можно подписаться и отписаться на странице автора. 
    - При подписке рецепты автора добавляются на страницу "Мои подписки" и удаляются оттуда при отказе от подписки. 
5. Страница "Избранное": 
    - На странице рецепта можно добавить рецепт в список избранного и удалить его оттуда. 
    - На любой странице со списком рецептов можно добавить рецепт в список избранного и удалить его оттуда. 
6. Страница "Список покупок": 
    - На странице рецепта можно добавить рецепт в список покупок и удалить его оттуда. 
    - На любой странице со списком рецептов можно добавить рецепт в список покупок и удалить его оттуда. 
    - Есть возможность выгрузить файл с перечнем и количеством необходимых ингредиентов для рецептов из "Списка покупок". 
    - Ингредиенты в выгружаемом списке не повторяются, корректно подсчитывается общее количество для каждого ингредиента. 
7. Страница "Создать рецепт": 
    - Есть возможность опубликовать свой рецепт. 
    - Есть возможность отредактировать и сохранить изменения в своем рецепте. 
    - Есть возможность удалить свой рецепт. 
8. Есть возможность выйти из системы. 
 
# Описание функционала для неавторизованных пользователей: 
 
1. Главная страница доступна для просмотра. 
2. Страница отдельного рецепта доступна для просмотра. 
3. Страница любого пользователя доступна для просмотра. 
4. Форма авторизации доступна и работает. 
5. Форма регистрации доступна и работает. 
 
# Описание функционала для администратора и админ-зоны: 
 
1. Все модели выведены в админ-зону. 
2. Для модели пользователей включена фильтрация по имени и email. 
3. Для модели рецептов включена фильтрация по названию, автору и тегам. 
4. На админ-странице рецепта отображается общее число добавлений этого рецепта в избранное. 
5. Для модели ингредиентов включена фильтрация по названию.

## Запуск проекта в dev-режиме

- Клонируйте репозиторий с проектом на свой компьютер. В терминале из рабочей директории выполните команду:
```bash
git clone git@github.com:Boris23-ops/foodgram-project-react.git
```

- Установить и активировать виртуальное окружение

```bash
python -m venv venv
source venv/Scripts/activate
```

- Установить зависимости из файла requirements.txt

```bash
python -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```
- Создать файл .env в папке проекта:
```.env
SECRET_KEY=secretkey
DEBUG=False
DJANGO_SERVER_TYPE=prod
ALLOWED_HOSTS=127.0.0.1,localhost,backend
POSTGRES_USER=postgre 
POSTGRES_PASSWORD=postgre
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432
```

### Выполните миграции:
```bash
python manage.py migrate
```

- В папке с файлом manage.py выполнить команду:
```bash
python manage.py runserver
```

- Создание нового супер пользователя 
```bash
python manage.py createsuperuser
```

### Загрузите статику:
```bash
python manage.py collectstatic --no-input
```
### Заполните базу тестовыми данными: 
```bash
python manage.py load_tags
python manage.py load_ingredients
```


## Запуск проекта через Docker

Установите Docker, используя инструкции с официального сайта:
- для [Windows и MacOS](https://www.docker.com/products/docker-desktop)
- для [Linux](https://docs.docker.com/engine/install/ubuntu/). Отдельно потребуется установть [Docker Compose](https://docs.docker.com/compose/install/)

Клонируйте репозиторий с проектом на свой компьютер.
В терминале из рабочей директории выполните команду:
```bash
git clone git@github.com:Boris23-ops/foodgram-project-react.git
```

- в Docker cоздаем образ :
```bash
docker build -t foodgram .
```

Выполните команду:
```bash
cd ../infra
docker-compose up -d --build
```

- В результате должны быть собрано три контейнера, при введении следующей команды получаем список запущенных контейнеров:  
```bash
docker-compose ps
```
Назначение контейнеров:  

|             IMAGES             | NAMES                |        DESCRIPTIONS         |
|:------------------------------:|:---------------------|:---------------------------:|
| borisrow23/foodgram_nginx      | infra-_nginx_1       |   контейнер HTTP-сервера    |
|         postgres:13            | infra-_db_1          |    контейнер базы данных    |
| borisrow23/foodgram_backend    | infra-_backend_1     | контейнер приложения Django |
| borisrow23/foodgram_frontend   | infra-_frontend_1    | контейнер приложения React  |


### Выполните миграции:
```bash
docker-compose exec backend python manage.py migrate
```
### Создайте суперпользователя:
```bash
docker-compose exec backend python manage.py createsuperuser
```

### Загрузите статику:
```bash
docker-compose exec backend python manage.py collectstatic --no-input
```

### Заполните базу тестовыми данными:
```bash
docker-compose exec backend python manage.py load_ingredients
docker-compose exec backend python manage.py load_tags   
```

### Автор:  
_[Короткиян Борис](https://github.com/Boris23-ops)_<br>