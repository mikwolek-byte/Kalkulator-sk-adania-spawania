# Kalkulator czasu warsztatowego Zekon

Lokalna aplikacja Python / Streamlit do obliczania składania i spawania. Normy składania: blacha 10 min/szt., profil dodatkowy 15 min/szt., profil główny 20 min/szt. Suma netto składania ×2. Spawanie: metry przejść ×8 min, następnie suma netto ×2,5. Brak minimum 1 mb. Współczynniki stosowane jeden raz. Masa w kg, wynik w rbg oraz rbg/t.

## Uruchomienie

Windows: zainstaluj Python 3.11 lub 3.12 i uruchom `uruchom.bat`. Pierwsze uruchomienie pobiera zależności. Aplikacja otworzy się w przeglądarce na tym komputerze.

Inne systemy:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Testy: `python -m unittest -v`.

## Praca

1. Wczytaj projekt JSON albo parę plików Eiffage (składanie i spawanie). Można też zacząć od pustego projektu i edytować tabele.
2. Sprawdź masę jednostkową i liczbę elementów wysyłkowych. Obmiar i liczba detali dotyczą jednej sztuki elementu.
3. Sprawdź klasyfikację detali. Import klasyfikuje wpisy „blacha…” jako blachę, a profile ze starą normą 20 jako główne. To propozycja do zatwierdzenia, nie reguła geometryczna.
4. Sprawdź długości i mnożniki przejść. Mnożnik to liczba odcinków × ściegi. Wartości I/J/L z Eiffage są już mnożnikami; nie dodawaj ściegów drugi raz. Puste I/J/L oznacza brak spoiny w danym kierunku zgodnie z dotychczasowym arkuszem. Brak wartości długości dla dodatniego mnożnika blokuje import.
5. Wyłącz spoiny wzdłużne profilu IKS, jeśli nie wchodzą w zakres. Zatwierdź obmiar. Pobierz projekt do dalszej pracy oraz wyniki CSV/JSON.

Brak zatwierdzenia, zerowa masa, nieznany element lub brak wymaganego parametru blokują wycenę.

## Zakres pierwszej wersji

Importuje jawne tabele kalkulacyjne Excel. Nie wykonuje automatycznego rozpoznawania spoin z PDF, DWG ani IFC. Same listy materiałowe nie opisują wszystkich połączeń. Obmiar nowych rysunków wymaga wprowadzenia lub zatwierdzenia przez kosztorysanta. W przykładach Eiffage szczegóły spoin są na niezałączonych rysunkach 199/200.

Domyślny wynik obejmuje podstawowe składanie i spawanie. Opcjonalnie można włączyć fazowanie, klinkowanie, dodatki i standardowy transport wewnętrzny z Excela oraz grzanie 5 min/m. Progi transportu odtworzono z przekazanych plików. Ręczne korekty sum, wynik 2899 min i transport ×4 nie są importowane. Brak zaokrągleń w obliczeniach netto. Wynik zaokrąglony jest tylko do prezentacji.

Długości w G/H/K arkusza są długościami obmiaru, które mogą różnić się od pełnego obrysu blachy. Nie zastępuj ich automatycznie wymiarami BOM. Nowe normy 10/15/20 i 8 min celowo zmieniają historyczne wyniki; starych sum nie należy traktować jako oczekiwanych wyników nowej metody.

## Architektura

- `engine.py`: walidacja i niezależny silnik kalkulacyjny.
- `import_eiffage.py`: adapter źródłowych arkuszy i standardowe progi transportu.
- `app.py`: import, edycja, zatwierdzanie i eksport.
- `test_engine.py`: testy jednostek, powtórzeń, współczynników, braków i wyłączeń.

Model danych: `elements` (identyfikator, sztuki i masa jednostkowa), `assembly` (rodzaj i liczba detali), `welds` (długość, powtórzenia i mnożnik przejść). Każda pozycja obmiaru ma źródło i stan zatwierdzenia. Suma rbg/t jest liczona jako suma rbg / suma ton, a nie średnia wskaźników.

## Repozytorium

Repozytorium: `mikwolek-byte/Kalkulator-sk-adania-spawania`. Pobierz kod przez Code → Download ZIP, rozpakuj i uruchom `uruchom.bat`. Nie dodawaj rysunków, ofert ani danych klientów do publicznego repozytorium. Sam kod nie zawiera załączników referencyjnych.
