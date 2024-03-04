# Foodgram
![Workflow](https://github.com/Boris23-ops/kittygram_final/actions/workflows/main.yml/badge.svg)
_
## api_Foodgram
Пример запущенного сервиса: 
[foo0dgram.ddns.net](https://foo0dgram.ddns.net)

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