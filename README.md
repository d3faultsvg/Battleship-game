# Battleship-game

FUNKCJONALNOŚC PROGRAMU

Program to klasyczna gra w „Statki” (Battleship) przeznaczona dla dwóch graczy w sieci lokalnej (LAN) lub na jednym komputerze.

Faza Rozstawiania:

Gracz widzi swoją planszę i układa na niej flotę: 1x pięciomasztowiec, 1x czteromasztowiec, 2x trójmasztowce, 1x dwumasztowiec.

Można zmieniać orientację statków (poziomo/pionowo) klawiszem R.

Logika kolizji: Gra pilnuje, aby statki nie nachodziły na siebie ani nie wychodziły poza planszę.
Co ważne – kod wymusza odstęp co najmniej jednej kratki między statkami (nie mogą się stykać bokami).

Faza Gry (Multiplayer):

Po rozstawieniu gra łączy się z serwerem i czeka na drugiego gracza.
System turowy: Serwer decyduje, kto strzela.
Gracz klika na planszę przeciwnika.

Informacja zwrotna:

Kolory: Szary (twój statek), Niebieski (woda), Czerwony (trafienie), Biały/Jasnoszary (pudło).

Statusy: Tekst na dole ekranu informuje o: "Trafiony", "Pudło", "Trafiony zatopiony" oraz o wygranej/przegranej.

Architektura: To tzw. Authoritative Server. Klient tylko wysyła współrzędne kliknięcia, a to serwer wie, gdzie są statki i decyduje, czy był traf, zapobiegając w ten sposób oszukiwaniu.
