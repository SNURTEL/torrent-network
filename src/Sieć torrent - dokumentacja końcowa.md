# **Projekt - Programowanie Sieciowe** 

## *Rekonstrukcja sieci torrentopodobnej*

#### Autorzy projektu

* Miłosz Mizak
* Tomasz Owienko
* Albert Torzewski
* Milan Wróblewski

## 1. Opis projektu i implementacji

### Opis projektu
Przedmiotem projektu jest skonstruowanie prostej sieci *torrentopodobnej* - pozwalające na skoordynowane, ale i rozproszone przesyłanie plików w sposób zbliżony do tego, jak odbywa się to w rzeczywistych tego rodzaju sieciach.

### Opis architektury

Na rozwiązanie zadania składją się dwa moduły - peera oraz koordynatora. 
Podczas działania projektu istnieje jednen koordynator pełniący rolę serwera oraz N peerów.
Peery komunikją się z koordynatorem w celu zestawinia połączenia z porządanym przez siebie innym peerem w celu pobrania pliku.
Podczas gdy peer rozpoczyna pobiernie pliku w osobnym procesie uruchamiany jest serwer raportujący na bieżąco dostępność w celu podtrzymania tej funkcjonalności.

## 2. Scenariusze komunikacji

### Kuminikacja peer - koordynator
- Peer odpytuje koordynatora o dostępność wybranego pliku - koordynator odpowiada w sotsowny sposób 
- Peer okresowo raportuje o dostępności plików posiadanych lokalnie

### Komunikacja peer - peer
- Jeden z peerów pobiera wybrany plik od drugiego peera


## 3. Definicje komunikatów

### Rodzaje wiadomości
- Błąd (`ERROR` - 0)
- Odpytanie koordynatora o dostępność pliku (`APEER` - 1)
- Informacja o dostępności od koordynatora (`PEERS` - 2)
- Raportowanie dostępności pliku (`REPRT` - 3)
- Odpytanie peera o dostępne chunki (`ACHNK` - 4)
- Informacja o dostępności chunków od peera (`CHNKS` - 5)
- Prośba o przesłanie chunka (`GCHNK` - 6)
- Przesłanie chunka (`SCHNK` - 7)


### Struktura wiadomości

#### ERROR - Stały rozmiar
1B rodzaj wiadomości
1B kod błędu
2B padding

#### APEER - Stały rozmiar
1B rodzaj wiadomości
3B padding
32B hash pliku

#### PEERS - Zmienny rozmiar
1B rodzaj wiadomości
3B padding
32B hash pliku
4B rozmiar pliku
4B liczba peerów
N*5B rekordy:
8B adres peera
1B rodzaj dostępności (1 - cały, 2 - cześć)

#### REPRT - Stały rozmiar
1B rodzaj wiadomości
3B padding
32B hash pliku
1B dostępność (0 - nie ma, 1 - częściowa, 2 - cały)
3B padding
4B rozmiar pliku

#### ACHNK - Stały rozmiar
1B rodzaj wiadomości
3B padding
32B hash pliku

#### CHNKS - Zmienny rozmiar
1B rodzaj wiadomości
3B padding
32B hash pliku
2B liczba chunków
2B padding
N * 4B - numery posiadanych chunków

#### GCHNK - Stały rozmiar
1B rodzaj wiadomości
3B padding
32B hash pliku
2B numer chunka
2B padding

#### SCHNK - Stały rozmiar
1B rodzaj wiadomości
3B padding
32B hash pliku
2B numer chunka
2B padding
32B hash chunka
NB dane


## 4. Opis zachowania podmiotów komunikatów

### Koordynator

- Koordynator trzyma informacje o dostępności poszczególnych plików u peerów
- Koordynator odpowiada na zapytania peerów o dostępność plików 
- Informacje dostępności plików mają okres ważności i są usuwane po upływie tego okresu

### Peer

- Peery przesyłają pliki między sobą i raportują dostępność koordynatorowi
- Podczas pobierania pliku peery okresowo raportują które fragmenty już są pobrane
- Po zakończeniu pobierania cały plik raportowany jako dostępny
- Pliki przeznaczone do udostępniania przechowywane są w określonym katalogu
- Do pobierania plików peer wykorzystuje spreparowany plik .fileinfo zawierające hash pliku, rozmiar pliku i liczbę chunków
- Po usunięciu pliku raportujemy ten fakt koordynatorowi
- Podczas pobiernia pliku w osobnym procesie uruchamiany jest serwer raportujący na bieżąco dostępność plików

## 5. Wyniki testów

Wszytskie testy zgodnie z oczekiwaniami prezentują założone zachowanie programu w przypadku awarii lub błędu użytkownika.
Odpowiednie komunikaty są wyświetlane w terminalu informując o nietypowej sytuacji np. rządanie pliku, który nie jest posidany przez żadengo z peerów. 

### Przypadki testowe
- pobranie pliku od jednego peera - single_peer_download
- pobranie pliku od wielu peerów - multiple_peers_share
- pobieranie pliku przez wiele peerów naraz - multiple_peers_download
- udostępnianie pobranego pliku - dzieje się automatycznie w ramach innych testów
- pobieranie i jednoczesne udostępnianie pliku (pobranych już chunków) - jak wyżej
- próba pobrania usuniętego pliku - deleted_file
    - plik usunięty z wyłączoną aplikacją
    - plik usunięty z włączoną aplikacją
- peer został wyłączony (koordynator inwaliduje wpis)
- koordynator nie żyje [*] - dead_coordinator

## 6. Podsumowanie

Projekt ten jest udanym przykładem implementacji podstawowych zasad działania sieci torrentopodobnej, w tym funkcje monitorowania, raportowania i zarządzania komunikacją. Osiągnięcia projektu pozwoliły nam zrozumieć zasady działania sieci P2P oraz jak realizować taką komunikację z poziomu kodu.