# Dokumentacja uruchomienia i testowania aplikacji

## 1. Uruchomienie aplikacji

### Wymagania wstępne

Przed uruchomieniem aplikacji upewnij się, że masz zainstalowane:

- Python 3.8 lub nowszy

- Menedżer pakietów pip

### Instrukcja uruchomienia

1. Sklonuj repozytorium projektu lub pobierz pliki aplikacji.

2. Przejdź do katalogu z projektem:

```cd /fast1```

3. Zainstaluj wymagane zależności:
Upewnij się, że w katalogu znajduje się plik requirements.txt. Następnie uruchom:

```pip install -r requirements.txt```

4. Utwórz i zainicjuj bazę danych SQLite:
Aplikacja automatycznie utworzy plik bazy danych orders.db przy pierwszym uruchomieniu, korzystając z modelu zdefiniowanego w aplikacji.

5. Uruchom aplikację:

```uvicorn main:app --reload```

Sprawdź dostępność aplikacji:
Po uruchomieniu aplikacja będzie działać domyślnie pod adresem:
http://127.0.0.1:8000

7. Przeglądaj dokumentację API:
Aplikacja oferuje dokumentację w formacie OpenAPI, dostępną pod adresem:

- http://127.0.0.1:8000/docs (Swagger UI)

- http://127.0.0.1:8000/redoc (Redoc UI)

# 2. Testowanie aplikacji (na przykładzie użycia Postmana)

### Konfiguracja Postmana

1. Otwórz Postmana i utwórz nowy zbiór (Collection), np. "Order Management API".

2. Skonfiguruj poszczególne żądania HTTP zgodnie z opisem poniżej.

### Testowanie poszczególnych endpointów

**a) POST /orders/ - Tworzenie zamówienia**

1. Wybierz metodę POST i ustaw URL:

```http://127.0.0.1:8000/orders/```

2. Przejdź do zakładki Body > raw i wybierz format JSON.

3. Wprowadź dane zamówienia, np.:
```
{
    "customer_name": "John Doe",
    "total_amount": 150.0,
    "currency": "EUR"
}
```
4. Kliknij Send.

5. Sprawdź odpowiedź:
```
{
    "id": 1,
    "customer_name": "John Doe",
    "total_amount": 150.0,
    "converted_amount": 33.3,
    "currency": "EUR",
    "status": "pending"
}
```
_(wartość converted_amount zależy od aktualnego kursu wymiany walut pobranego z API NBP
i waluty docelowej określonej w "currency")_

**b) PUT /orders/{order_id}/ - Aktualizacja statusu zamówienia**

1. Wybierz metodę PUT i ustaw URL:

```http://127.0.0.1:8000/orders/1/```

_(Zmień 1 na ID zamówienia, które chcesz zaktualizować.)_

2. Przejdź do zakładki Body > raw i wybierz format JSON.

3. Wprowadź nowy status, np.:
```
{
    "status": "shipped"
}
```
4. Kliknij Send.

5. Sprawdź odpowiedź:
```
{
    "id": 1,
    "customer_name": "John Doe",
    "total_amount": 150.0,
    "converted_amount": 33.3,
    "currency": "EUR",
    "status": "shipped"
}
```
**c) GET /orders/{order_id}/ - Pobranie szczegółów zamówienia**

1. Wybierz metodę GET i ustaw URL:

```http://127.0.0.1:8000/orders/1/```

_(Zmień 1 na ID zamówienia, które chcesz pobrać.)_

2. Kliknij Send.

3. Sprawdź odpowiedź:
```
{
    "id": 1,
    "customer_name": "John Doe",
    "total_amount": 150.0,
    "converted_amount": 33.3,
    "currency": "EUR",
    "status": "shipped"
}
```
**d) GET /orders/ - Pobranie listy zamówień**

1. Wybierz metodę GET i ustaw URL:

```http://127.0.0.1:8000/orders/```

2. Kliknij Send.

3. Sprawdź odpowiedź:
```
[
    {
        "id": 1,
        "customer_name": "John Doe",
        "total_amount": 150.0,
        "converted_amount": 33.3,
        "currency": "EUR",
        "status": "shipped"
    }
]
```
**e) Obsługa błędów**

Przetestuj sytuacje, w których powinny być zwracane błędy, np.:

- **Próba pobrania nieistniejącego zamówienia:**
Wynik: 404 Not Found.

- **Podanie nieprawidłowej waluty (np. "XYZ") w zamówieniu:**
Wynik: 502 Bad Gateway z komunikatem o błędzie.