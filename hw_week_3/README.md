# otus.py.scoring_api

Default port ```8080```, all requests send to url   ```/method/```

1. To start server run ```python3 server.py```
2. To avoid ```Forbidden``` response just paste right token from console output, from string, begging from ```DIGEST```

Example requests:

```curl -X POST -H "Content-Type: application/json" -d '{"account": "horns&hoofs", "login": "admin", "method": "online_score", "token": "c40ff9c8cc31db195bde42d9e24c0d660e61e2cbe7161777ec7c41dede9c8f6c475ce98a836d93b8fb5f48967666b8f3b3d9a8f0334499cec4fb8e387b76b4ab", "arguments": {"phone": "79265031763", "email": "tihonich@mail.ru", "first_name": "Oleg", "last_name": "Tikhonov", "birthday": "24.08.1983", "gender": 1}}' http://127.0.0.1:8080/method/```


```curl -X POST -H "Content-Type: application/json" -d '{"account": "horns&hoofs", "login": "admin", "method": "clients_interests", "token": 	"c40ff9c8cc31db195bde42d9e24c0d660e61e2cbe7161777ec7c41dede9c8f6c475ce98a836d93b8fb5f48967666b8f3b3d9a8f0334499cec4fb8e387b76b4ab", "arguments": {"client_ids": [1,2,3,4], "date": "24.08.1983"}}' http://127.0.0.1:8080/method/```