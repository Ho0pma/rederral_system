Цель проекта: реализовать API для реферальной системы

Запуск: в корне проекта прописать **docker compose up --build**

Автоматически создастся superuser: 
  - login: test@mail.ru
  - pass: root

urls:
для всех пользователей:
  - аутентификация: http://localhost/login/    
  - регистрация: http://localhost/register/
    
только для аутентифицированных:
  - мейн страница: http://localhost

только для админа (test@mail.ru):
  - инфа по всем пользователям: http://localhost/users/
  - detail по одному: http://localhost/users/?email=SEARCHED_EMAIL (ex: http://localhost/users/?email=test@mail.ru)
  - посмотреть рефералов пользователя: http://localhost/users/<int:pk> (ex: http://localhost/users/1)
    

PS: 
  - реферальный код истекает через 1 минуту (поставил так, чтобы тестировать)
