# **Projekt - Programowanie Sieciowe** 

## *Rekonstrukcja sieci torrentopodobnej*

#### Autorzy projektu

* Miłosz Mizak
* Tomasz Owienko
* Albert Torzewski
* Milan Wróblewski

## 1. Założenia (architektura)

Przedmiotem projektu jest skonstruowanie sieci *torrentopodobnej*. Ze względu na dowolność rozwiązania, postanowiliśmy poczynić założenia architektoniczne sieci.

W naszej wersji sieci będą występowały dwa rodzaje użytkowników - 1 *koordynator* oraz dowolna liczba *peerów*. 

System korzystać będzie z adresacji IPv4, w roli protokołu warstwy transportowej wykorzystany zostanie protokół TCP.

### Koordynator

- Koordynator trzyma informacje o dostępności poszczególnych części plików
- Pliki są podzielone na chunki stałego rozmiaru
- Plik identyfikowany przez hash SHA256 oraz jego długość w bajtach
- Koordynator nie odpytuje peerów o dostępność plików
- Informacje o dostępności plików mają okres ważności

### Peer

- Peery przesyłają pliki między sobą i raportują dostępność koordynatorowi
- Maksymalna liczba otwartych jednocześnie połączeń jest parametrem peera
- Podczas pobierania pliku peery okresowo raportują które fragmenty już są pobrane
- Po zakończeniu pobierania cały plik raportowany jako dostępny
- Pliki przeznaczone do udostępniania przechowywane są w określonym katalogu
- Peer musi znać hash pliku żeby go pobrać - problem wyszukiwania plików poza zakresem projektu
- Zamknięcie aplikacji klienta wymusza pobranie plików częściowo skompletowanych od nowa (nie przechowujemy stanu pobierania)
- Po uruchomieniu klienta od razu usuwamy wszystkie pliki częściowo skompletowane
- Po usunięciu pliku raportujemy ten fakt koordynatorowi
- Jeśli jakiś peer zapyta nas o plik/chunk którego nie mamy, raportujemy koordynatorowi
- Peery nawiązują połączenia na stałych portach, a po nawiązaniu połączenia otwierają nowe (efemeryczne) porty, na których przebiera *faktyczna* komunikacja

### Raportowanie dostępności

Peer może zaraportować koordynatorowi:
- Posiadanie całości pliku
- Nieposiadanie pliku
- Posiadanie części chunków pliku

Raportowanie odbywa się:
- Po uruchomieniu aplikacji klienta (raportujemy pliki dostępne w całości)
- Podczas pobierania pliku (raportujemy dostępność poszczególnych części)
- Po pobraniu pliku (raportujemy dostępność całości)
- Okresowo co T sekund

Raportujemy dostępność przez wysłanie:
- Hasha pliku 
- Rozmiaru pliku
- Liczby chunków
- Faktu posiadania części bądź wszystkich chunków
- Wektora binarnego reprezentującego listę chunków dostępnych u danego peera

## 2. Zakres realizacji

Wobec powyższych założeń należy zaimplementować:
- działanie koordynatora
- działanie peerów - pobieranie plików, ich seedowanie oraz moduł raportujący

## 3. Przypadek użycia

Poniżej opisany jest typowy przypadek użycia. 

1. Peer odpytuje koordynatora o dostępność pliku na podstawie hasha
2. Koordynator zwraca:
    - Nazwę pliku
    - Rozmiar pliku
    - Liczbę chunków
    - Hashe poszczególnych chunków
    - Listę peerów posiadających plik w całości bądź częściowo
3. Jeśli któreś peery posiadają plik częściowo, klient odpytuje je, które chunki posiadają
4. Klient decyduje, od których peerów chce pobierać które chunki
	- Peer będzie próbował pobierać najpierw najrzadsze chunki - dzięki takiemu rozwiązaniu pliki powinny szybko się rozpropagować po sieci
    - Jeśli jakieś chunki nie są jeszcze dostępne, ich pobieranie zostanie ponowione po pobraniu dostępnych już chunków
6. Klient rezerwuje przestrzeń na dysku (tworzy pusty plik o zadanym rozmiarze)
    - plik otrzymuje sufiks `.partial` żeby nie pomylić go z plikiem już skompletowanym
7. Klient otwiera połączenia do wybranych peerów i prosi o przesłanie poszczególnych chunków
    - Jeśli peer nie może wysłać jakiegoś chunka, umieszczany jest on na końcu kolejki
8. Peery przesyłają chunki razem z ich numerami i hashami
9. Po otrzymaniu każdego chunka odbiorca sprawdza jego hash
    - Jeśli się zgadza, wpisujemy w odpowiednie miejsce w pliku (możemy je obliczyć, bo znamy rozmiar jednego chunka i numer otrzymanego)
    - Jeśli się nie zgadza, zostaje umieszczony na końcu kolejki
10. Po pobraniu pierwszego chunka peer raportuje koordynatorowi, że posiada część pliku
11. Co N chunków (albo co N sekund) peer odpytuje koordynatora o dostępność pliku (czy się zmieniła)
12. Jeśli po zakończeniu pobierania brakuje jakichś chunków (błędy), koordynator jest ponownie odpytywany o dostępność i cały proces się powtarza
13. Kiedy pobrano cały plik oraz jego hash jest poprawny, peer po raz ostatni raportuje dostępność i usuwa sufiks `.partial`
14. Jeżeli okaże się, że hash pliku końcowego nie zgadza się z dostarczonym hashem, peer sprawdza po kolei hashe wszystkich chunków. Jeżeli te hashe będą zgodne, peer zakłada, że plik jest niepoprawny należy poinformować o tym użytkownika i pobrać plik ponownie. Jeżeli jakiś chunk faktycznie jest błędny, to pytamy o niego u koordynatora i proces się powtarza

## 4. Obsługa sytuacji błędnych

Błędy mogą wystąpić na wielu różnych etapach procesu. Poniżej przedstawiamy typowe błędy:
- hash chunka nie zgadza się z naszym wyliczonym hashem - pobieramy plik jeszcze raz
- hash pliku nie zgadza się z naszym wyliczonym hashem - sprawdzamy poprawność chunków. Jeżeli któryś jest wadliwy, to pobieramy go ponownie, w przeciwnym przypadku usuwamy plik i rozpoczynamy jego pobieranie od początku
- koordynator nie otrzymał od dłuższego czasu informacji od peera - koordynator inwaliduje wpis, aby zapobiec pobieraniu wadliwych plików
- nieudana próba wysłania żądanego pakietu - zaprzestanie transmisji i oczekiwanie na ponowne żądanie
- brak pliku o żądanym hashu - przesłanie odmowy oraz przekazanie koordynatorowi informacji o nieaktualnym stanie dostępności
- brak dostępności koordynatora - zaprzestanie rozsyłania i pobierania pakietów w celu uniknięcia utraty danych. Okresowe odpytywanie koordynatora o stan dostępności.
- nieskuteczne wysłanie żądania o plik - koordynator weryfikuje dostępność peera i potencjalnie usuwa wpis jeśli peer się rozłączył

## 5. Przypadki testowe

- pobranie pliku od jednego peera
- pobranie pliku od wielu peerów
- pobieranie pliku przez wiele peerów naraz
- udostępnianie pobranego pliku
- pobieranie i jednoczesne udostępnianie pliku (pobranych już chunków)
- próba pobrania usuniętego pliku
    - plik usunięty z wyłączoną aplikacją
    - plik usunięty z włączoną aplikacją
- peer został wyłączony (koordynator inwaliduje wpis)
- koordynator nie żyje [*]

## 6. Scenariusz demonstracji

Demonstracja działania sieci będzie polegała na uruchomieniu przypadków testowych. Peery oraz koordynator zostaną uruchomione we własnych kontenerach przy pomocy narzędzia `docker compose`.
