Napisz zestaw dwóch programów – klienta i serwera wysyłające datagramy UDP. Wykonaj
ćwiczenie w kolejnych inkrementalnych wariantach (rozszerzając kod z poprzedniej wersji).

## 1.1
Klient wysyła, a serwer odbiera datagramy o stałym rozmiarze (rzędu kilkuset bajtów). Datagramy powinny posiadać ustaloną formę danych. Przykładowo: pierwsze dwa bajty datagramu mogą zawierać informację o jego długości, a kolejne bajty kolejne litery A-Z powtarzające się wymaganą liczbę razy (ale można przyjąć inne rozwiązanie, można też przesyłać dane binarne, tj. nie napisy i nie wyłącznie ASCII). Odbiorca powinien weryfikować odebrany datagram i odsyłać odpowiedź (potwierdzenie) o ustalonym formacie.

Wykonać program w dwóch wariantach: C oraz Python. Sprawdzić i przetestować działanie „między-platformowe”, tj. klient w C z serwerem Python i vice versa.

## 1.2
Na bazie kodu z zadania 1.1 napisać klienta, który wysyła kolejne datagramy o przyrastającej
wielkości np. 1, 100, 200, 1000, 2000... bajtów. Sprawdzić, jaki był maksymalny rozmiar
wysłanego (przyjętego) datagramu. Ustalić z dokładnością do jednego bajta jak duży datagram jest obsługiwany. Wyjaśnić.

To zadanie można wykonać, korzystając z kodu klienta i serwera napisanych w C lub w Pythonie (do wyboru). Nie trzeba tworzyć wersji w obydwu językach.

## 1.3
Uruchomić program z przykładu 1.1 w środowisku symulującym błędy gubienia pakietów.
(Informacja o tym jak to zrobić znajduje się w skrypcie opisującym środowisko Dockera).
Rozszerzyć protokół i program tak, aby gubione pakiety były wykrywane i retransmitowane.
