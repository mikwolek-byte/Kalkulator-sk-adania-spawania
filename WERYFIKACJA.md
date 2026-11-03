# Sprawdzenie pierwszej wersji

Przeprowadzono osiem testów silnika: jednostki i ilości, jednorazowe współczynniki, brak minimum 1 m, brakujące dane, zatwierdzanie obmiaru, błędne masy, wyłączone spoiny, brak modyfikacji danych i opcjonalne grzanie.

Sprawdzono import obu przekazanych skoroszytów referencyjnych: oznaczenia elementów, ilości, masy oraz obmiar składania i spawania. Zweryfikowano zastosowanie nowych norm 10/15/20 min/szt. oraz 8 min/m i współczynników 2 i 2,5. Import przelicza obmiar z Excela; nie stanowi ponownej walidacji oznaczeń spoin z rysunków. Danych projektowych nie zamieszczono w repozytorium.

Składnia modułów oraz osiem testów silnika przeszły kontrolę. Na runnerze Windows wykonano test interfejsu Streamlit: uruchomienie, zatwierdzenie obmiaru i sprawdzenie wyników składania oraz spawania. Zbudowano jednoplikowy KalkulatorZekon.exe i sprawdzono uruchomienie jego lokalnego serwera oraz dostępność strony aplikacji przez HTTP. Test serwera EXE nie zastępuje pełnego testu interaktywnego interfejsu wewnątrz spakowanego programu. Wersja EXE nie wymaga instalacji Pythona. Osobny test importu rzeczywistych skoroszytów wykonano wcześniej ze źródeł.

Załączniki źródłowe i dane klientów nie są zawarte w paczce kodu.
