
## 2.1

### C

W tej części zadania należało stworzyć klienta napisanego w C, który będzie wysyłał podaną strukturę danych do serwera. W naszym przypadku na strukturę danych wybraliśmy listę jednokierunkową.

Pojedynczy węzeł w liście jest reprezentowany za pomocą następującej struktury:

```c
typedef struct node {  
    struct node *next;  // 8B  
    uint16_t short_val; // 2B  
    // +2B align    
    uint32_t int_val;  // 4B  
    char fixed_string[6];  // 6B  
    // +2B align    
    uint32_t dynamic_string_length;  // 4B  
    char dynamic_string[];  // 0B  
} node;  // total = 24B + 4B align = 28B
```

W pliku *linked_list.h* znajdują się metody, które wypełniają tę strukturę odpowiednimi danymi, tworząc listę jednokierunkową. Znajduje się tam także destruktor listy.

Komunikacja z serwerem przebiega następująco:
- klient wysyła najpierw długość listy, a więc ilość węzłów
- następnie po kolei wysyłane są wszystkie węzły aż do wyczerpania listy
- podczas wysyłania listy generowane są komentarze informujące o stanie wysyłanych węzłów.

Jako, że węzły mogą mieć różną długość, zależną od pola `dynamic_string`, to musi to być uwzględnione podczas wysyłki tych węzłów. Wielkość pakietu określa się poprzez wyrażenie `sizeof(node)+ current_node->dynamic_string_length`. 

Niezależnie od tego czy uda się przesłać całą listę, zawsze pod koniec działania programu zamykane jest gniazdo służące do komunikacji z serwerem oraz usuwana jest lista jednokierunkowa.

Przykładowy wynik działania programu:

```
Connected to server, sending data...
Sent list length!
id: 0, short_val: 0, int_val: 0, fixed_string: abcdef, dynamic_string: a 
Sent node of id 0
id: 1, short_val: 1, int_val: 2, fixed_string: abcdef, dynamic_string: aa 
Sent node of id 1
id: 2, short_val: 2, int_val: 4, fixed_string: abcdef, dynamic_string: aaa 
Sent node of id 2
id: 3, short_val: 3, int_val: 6, fixed_string: abcdef, dynamic_string: aaaa 
Sent node of id 3
id: 4, short_val: 4, int_val: 8, fixed_string: abcdef, dynamic_string: aaaaa 
Sent node of id 4
Sent the linked list!
```


### Python

Serwer napisany w języku python odbierający listę zdefiniowaną przez klienta. 
Serwer domyślnie nasłuchuje na localhost :8000 lecz przygotowana została możliwość zmiany poprzez podanie argumentów wywołania w konsoli.
Serwer będzie odbierał dane w pętli aż do wywołania przerwania systemowego, oraz odebrane dane z poszczególnych list wypisywał do konsoli.

```
python3 server.py
Using :8000
Server listening on port 8000
Connection from ('127.0.0.1', 61794)
List length is 5
Received linked list:
(0, 0, 'abcdef', 1, 'a')
(1, 2, 'abcdef', 2, 'aa')
(2, 4, 'abcdef', 3, 'aaa')
(3, 6, 'abcdef', 4, 'aaaa')
(4, 8, 'abcdef', 5, 'aaaaa')
```


## 2.2

W kodzie dokonano dwóch zmian:
- w *networking.h* podmieniono parametr `ai_family` z `AF_INET` na `AF_INET6`
- w *server.py* podmieniono parametr w konstruktorze gniazda z `AF_INET` na `AF_INET6`

Aby wywołać program dla localhost, trzeba w tym przypadku użyć adresu ::1.

## 2.3c

Zaimplementowano współbieżny wariant serwera w oparciu o `ThreadPoolExecutor`. Serwer oczekuje na nowe połączenia (`.accept(...)`), a  w momencie pojawienia się takowego przekazuje je do osobnego wątku:

```python3
with ProcessPoolExecutor(max_workers=8) as executor:
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        executor.submit(handle_connection, client_socket, addr, log_prefix = f"[{i}] ")
```

Funkcja obsługi pojedynczych połączeń pozostała bez zmian. Należy zauważyć, że pomimo wydzielenia osobnego wątku na każde połączenie, cały serwer korzysta z tylko jednego procesu, gdyż taka jest istota działania `ThreadPoolExecutor` - dla zapewnienia faktycznej równoległości należałoby skorzysać z klasy `ProcessPoolExecutor`, która może wydzielić obsługę poszczególnych połączeń do osobnych procesów. Byłoby to jednak rozwiązanie dalekie od optymalnego - tak wydzielone procesy przez większość czasu i tak byłyby zajęte oczekiwaniem na dane od klienta, co czyniłoby je porównywalnie efektywnymi z wątkami przy jednoczesnym dużo wyższym koszcie wydzielenia osobnego procesu, niż wątku.

#### Konfiguracja testowa
Serwer oraz klienty uruchomiono w osobnych kontenerach przy użyciu Docker Compose. Do utworzenia wielu klientów skorzystano z parametru `mode: replicated; replicas: X`. Aby ułatwić śledzenie działania programu, wprowadzono opóźnienie pomiędzy przesyłaniem kolejnych węzłów listy wielkości 1s +/- 0.5s (losowo).

Przetestowano dwa scenariusze działania:

#### Liczba wątków przewyższa liczbę klientów

Klienty obsługiwane są w czasie rzeczywistym, a każdy z nich otrzymuje własny wątek do obsługi połączenia, a praca przebiega bez zakłóceń:

```
23-client-5  | Connected to server, sending data...
23-client-5  | Sent list length!
z33_server   | Connection from ('172.26.0.4', 46682)
z33_server   | [2] List length is 100
23-client-2  | Connected to server, sending data...
23-client-2  | Sent list length!
z33_server   | Connection from ('172.26.0.5', 52238)
z33_server   | [3] List length is 100
23-client-3  | Connected to server, sending data...
23-client-3  | Sent list length!
z33_server   | Connection from ('172.26.0.6', 54916)
z33_server   | [4] List length is 100
23-client-6  | Connected to server, sending data...
23-client-6  | Sent list length!
```

#### Liczba klientów przewyższa liczbę wątków

W takim scenariuszu część połączeń nie jest obsługiwana, dopóki obsługa poprzednich się nie zakończy:

```
23-client-1  | Sent node of id 11
23-client-1  | id: 12, short_val: 12, int_val: 24, fixed_string: abcdef, dynamic_string: aaaaaaaaaaaaa 
23-client-1  | Sent node of id 12
23-client-5  | id: 12, short_val: 12, int_val: 24, fixed_string: abcdef, dynamic_string: aaaaaaaaaaaaa 
23-client-5  | Sent node of id 12
z33_server   | [1] (12, 24, 'abcdef', 13, 'aaaaaaaaaaaaa')
23-client-2  | id: 13, short_val: 13, int_val: 26, fixed_string: abcdef, dynamic_string: aaaaaaaaaaaaaa 
23-client-2  | Sent node of id 13
z33_server   | [2] (13, 26, 'abcdef', 14, 'aaaaaaaaaaaaaa')
z33_server   | [2] (14, 28, 'abcdef', 15, 'aaaaaaaaaaaaaaa')
23-client-2  | id: 14, short_val: 14, int_val: 28, fixed_string: abcdef, dynamic_string: aaaaaaaaaaaaaaa 
23-client-2  | Sent node of id 14
```

Co istotne, pozostałe klienty w dalszym ciągu przesyłają dane do buforów - bufory te są opróżnione (bez oczekiwania) po odblokowaniu dotychczas zajętych wątków:

```
23-client-2  | id: 99, short_val: 99, int_val: 198, fixed_string: abcdef, dynamic_string: aaaaaaaaaaaaa<*>
23-client-2  | Sent node of id 99
23-client-2  | Sent the linked list!
23-client-2  | free(): invalid pointer
z33_server   | [2] (98, 196, 'abcdef', 99, 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa<*>
z33_server   | [2] (99, 198, 'abcdef', 100, 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa<*>')
z33_server   | [2] Received linked list:
z33_server   | (0, 0, 'abcdef', 1, 'a')
z33_server   | (1, 2, 'abcdef', 2, 'aa')
z33_server   | (2, 4, 'abcdef', 3, 'aaa')
z33_server   | (3, 6, 'abcdef', 4, 'aaaa')
z33_server   | (4, 8, 'abcdef', 5, 'aaaaa')
z33_server   | (5, 10, 'abcdef', 6, 'aaaaaa')
z33_server   | (6, 12, 'abcdef', 7, 'aaaaaaa')
z33_server   | (7, 14, 'abcdef', 8, 'aaaaaaaa')
z33_server   | (8, 16, 'abcdef', 9, 'aaaaaaaaa')

```
