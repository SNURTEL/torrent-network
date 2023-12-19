Napisać zestaw programów – klienta i serwera – komunikujących się poprzez TCP. Wykonać
ćwiczenie w kolejnych inkrementalnych wariantach, rozszerzając kod z poprzedniej wersji.

## 2.1
Napisać w języku C/Python klienta TCP, który wysyła złożoną strukturę danych, np. utworzoną w pamięci listę jednokierunkową lub drzewo binarne struktur zawierających (oprócz danych organizacyjnych) pewne dane dodatkowe, np. liczbę całkowitą 16-bitową, liczbę całkowitą 32-bitową oraz napis zmiennej i ograniczonej długości. Serwer napisany w Pythonie/C powinien te dane odebrać, dokonać poprawnego „odpakowania” tej struktury i wydrukować jej pola (być może w skróconej postaci, aby uniknąć nadmiaru wyświetlanych danych). Klient oraz serwer powinny być napisane w różnych językach.

Wskazówka: można wykorzystać moduły Pythona: struct i io.

## 2.2

Zmodyfikować programy z zadania 2.1 tak, aby posługiwały się IPv6.

## 2.3c (wersja dla naszej grupy)

Na bazie wersji 2.1 zmodyfikować serwer tak, aby miał konstrukcję współbieżną, tj. obsługiwał każdego klienta w osobnym procesie. Przy czym:

- Dla C należy posłużyć się funkcjami fork() oraz (obowiązkowo) wait().
- Dla Pythona posłużyć się wątkami, do wyboru: wariant podstawowy lub skorzystanie z ThreadPoolExecutor

Przetestować dla kilku równolegle działających klientów.