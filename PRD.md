# Dokument wymagań produktu (PRD) = PortMan (Portfolio Manager)

## 1.Przegląd produktu

PortMan to lekka aplikacja do lokalnego zarządzania portfelem inwestycyjnym (MVP), która pozwala na szybkie dodawanie i edycję transakcji, monitorowanie kluczowych KPI portfela oraz eksport danych do CSV. Celem jest zastąpienie arkuszy Excel prostym, spójnym narzędziem z poprawną logiką obliczeń (WAC, kontrola oversell) i wysoką użytecznością przy małej skali danych (~100 transakcji).

Zakres MVP obejmuje: CRUD transakcji (buy, sell, dividend, interest, flaga CFD), aktualizację cen bieżących per ticker (wpływ na unrealized P/L), KPI zależne od filtrów, tabelę transakcji z filtrami i sortowaniem, oznaczanie statusu buy jako niesprzedane/częściowo sprzedane (na podstawie wolumenu netto, WAC + oversell guard), eksport CSV, lokalną autoryzację (pojedynczy login). Brak użycia AI i brak funkcji poza wymienionym minimum.

Główna wartość: redukcja czasu i błędów związanych z ręcznym liczeniem w Excelu oraz zapewnienie spójnej, weryfikowalnej metodologii obliczeń z tolerancją zgodności ±0,01 PLN względem dotychczasowych arkuszy.

## 2. Problem użytkownika

Użytkownik obecnie zarządza portfelem w Excelu, co wymaga:
- ręcznego wprowadzania i utrzymywania formuł dla P/L (częste pomyłki, niespójności),
- braku wbudowanej kontroli nad sprzedażą powyżej posiadanego wolumenu,
- braku spójnego liczenia WAC i statusów pozycji po częściowych sprzedażach,
- trudności w szybkim podsumowaniu KPI przy różnych filtrach (np. tylko ETF, tylko ticker X),
- braku prostego eksportu i odtwarzalności danych.

Potrzeba: szybkie, bezbłędne dodawanie transakcji i natychmiastowe, poprawne przeliczenia KPI (realized/unrealized/total), z możliwością filtrowania widoku oraz prostym eksportem do CSV.

## 3. Wymagania funkcjonalne

3.1. Modele danych (MVP)
- Transakcja: id, data, ticker, typ (buy|sell|dividend|interest), ilość (dla buy/sell), cena (dla buy/sell), kwota (dla dividend/interest), waluta (domyślnie PLN), kategoria instrumentu (stock|ETF|bond|inne), flaga CFD (bool), notatka (opcjonalnie), status (aktywny), znacznik utworzenia/aktualizacji.
- Cena bieżąca: ticker, cena_aktualna, waluta, timestamp_aktualizacji.
- Użytkownik (autoryzacja lokalna): login, hash_hasła, timestamp_utworzenia.

3.2. CRUD transakcji
- Dodaj transakcję dla typów: buy, sell, dividend, interest; flaga CFD opcjonalna.
- Edytuj transakcję w modalu; po zapisaniu natychmiastowe przeliczenia.
- Usuń transakcję (twardo) — aktualizacja przeliczeń po usunięciu.
- Walidacje: brak wartości ujemnych; sell nie może przekroczyć posiadanego wolumenu (oversell blokowany).

3.3. Ceny bieżące i wpływ na P/L
- Formularz aktualizacji ceny bieżącej per ticker (ręczny input).
- Aktualizacja ceny przelicza Unrealized P/L i Total P/L dla pozycji danego tickera.

3.4. KPI portfela (respektują aktywne filtry)
- Invested: suma wartości transakcji buy (∑ ilość × cena) w zakresie widoku.
- Realized P/L: suma zysków/strat ze sprzedaży (na bazie WAC) + dywidend + odsetek.
- Unrealized P/L: dla aktualnie posiadanego wolumenu netto per ticker na podstawie WAC i ceny bieżącej.
- Total P/L: Realized P/L + Unrealized P/L.
- Prezentacja: kwota i % (definicja % w MVP: Total P/L / Invested, gdy Invested > 0; gdy 0, pokazać „—”).

3.5. Logika WAC i status pozycji
- WAC per ticker liczony z transakcji buy: WAC = (∑ ilość_buy × cena_buy) / (∑ ilość_buy).
- Sell redukuje wolumen posiadany; Realized P/L = ilość_sell × (cena_sell − WAC_w_momencie_sprzedaży).
- Po każdej sprzedaży wolumen posiadany = ∑ buy − ∑ sell; kontrola oversell blokuje transakcje sell powyżej posiadanego wolumenu.
- Statusy buy: niesprzedane/częściowo sprzedane (na podstawie wolumenu netto). W MVP utrzymujemy status na poziomie tickera (wymagane do KPI i walidacji), bez wizualnego rozbicia partii.

3.6. Tabela transakcji
- Filtry: ticker, typ (buy/sell/dividend/interest), status (np. tylko niesprzedane), kategoria instrumentu (stock/ETF/bond/CFD/itp.).
- Sortowanie: zysk/strata, ticker, data.
- Nieskończone przewijanie (paginated/infinite scroll) dla wygodnej nawigacji do ~100 transakcji.

3.7. Eksport CSV
- Pełny eksport transakcji do CSV. Minimalny zakres kolumn: id, data, ticker, typ, ilość, cena, kwota, waluta, kategoria, CFD, notatka.
- Nazewnictwo pliku: portman-transactions-YYYYMMDD-HHMM.csv (lokalny zapis).
- Opcjonalne w etapie 2: eksport snapshotu pozycji i/lub cen bieżących.

3.8. Autoryzacja lokalna
- Pojedynczy login użytkownika (lokalnie). Hasło przechowywane jako hash (algorytm do doprecyzowania: bcrypt/argon2).
- Sesja lokalna dla bieżącej instancji aplikacji (mechanizm sesji do uzgodnienia zależnie od stacku, np. Streamlit session state).

3.9. Użyteczność i wydajność
- Dodanie standardowej transakcji ≤ 20 s (od wejścia do zapisu).
- Płynna praca do ~100 transakcji bez odczuwalnych opóźnień.

3.10. Obsługa błędów i komunikaty
- Przy próbie oversell: komunikat o przekroczeniu dostępnego wolumenu oraz wskazanie ilości posiadanej.
- Przy braku ceny bieżącej: wyświetlić informację, że Unrealized P/L nie może zostać policzony dla danego tickera.
- Walidacje wejścia: wymagane pola per typ transakcji, formaty liczb/daty.

## 4. Granice produktu

W zakresie (MVP):
- CRUD transakcji (buy, sell, dividend, interest) z flagą CFD.
- Ręczna aktualizacja cen bieżących per ticker.
- KPI: Invested, Realized P/L, Unrealized P/L, Total P/L (kwota i %).
- Filtry, sortowanie, nieskończone przewijanie tabeli transakcji.
- Kontrola oversell i logika WAC per ticker.
- Eksport CSV transakcji.
- Lokalna autoryzacja (pojedynczy login).

Poza zakresem (MVP):
- Integracje z API maklerskimi lub zewnętrznymi źródłami cen (brak AI/API).
- Zaawansowane raporty i wykresy, analizy ryzyka, podatki.
- Pełna sekcja „Pozycje per ticker” jako osobny widok (opcjonalne w etapie 2; w MVP KPI i walidacje korzystają z agregacji per ticker bez rozbicia partii wizualnych).
- Zaawansowane role/poziomy uprawnień (tylko pojedynczy login).

Kwestie do doprecyzowania (następny etap):
- Techniczne szczegóły autoryzacji: metoda hashowania (bcrypt/argon2) i przechowywanie (np. SQLite), mechanizm sesji.
- Definicja % w KPI dla wariantów widoku (czy osobno dla realized/unrealized, lub odniesienia do WAC × posiadana ilość). W MVP: Total/Invested.
- Algorytm i prezentacja „pozostałej ilości” przy częściowych sprzedażach (interfejs).
- Schemat CSV dla cen bieżących i snapshotu pozycji (jeśli dodamy w etapie 2).
- Specyfika CFD w KPI (na razie etykieta, brak odmiennych reguł).

## 5. Historyjki użytkowników

US-001
Tytuł: Dodanie zakupu (buy)
Opis: Jako użytkownik chcę dodać transakcję kupna z ilością i ceną, aby zaktualizować Invested i posiadany wolumen oraz przygotować bazę do obliczeń WAC i P/L.
Kryteria akceptacji:
- Po zapisaniu buy Invested wzrasta o ilość × cena.
- WAC dla tickera aktualizuje się zgodnie z formułą z sekcji 3.5.
- Wolumen posiadany wzrasta o ilość transakcji.
- Transakcja widoczna w tabeli z poprawnymi danymi.

US-002
Tytuł: Częściowa sprzedaż (sell)
Opis: Jako użytkownik chcę dodać sprzedaż mniejszą lub równą posiadanemu wolumenowi, aby zaktualizować Realized P/L i wolumen posiadany, bez modyfikacji istniejących buy.
Kryteria akceptacji:
- Aplikacja blokuje sprzedaż powyżej posiadanego wolumenu (oversell).
- Realized P/L = ilość_sell × (cena_sell − WAC z momentu sprzedaży).
- Wolumen posiadany maleje o sprzedaną ilość.
- Buy pozostają niezmienione; status tickera aktualizuje się (niesprzedany/częściowo).

US-003
Tytuł: Pełna sprzedaż (zamknięcie pozycji)
Opis: Jako użytkownik chcę sprzedać całość posiadanego wolumenu, aby zrealizować P/L i wyzerować wolumen posiadany dla tickera.
Kryteria akceptacji:
- Po transakcji posiadany wolumen = 0.
- Realized P/L policzony wg WAC jak w US-002.
- Ticker nie wpływa na Unrealized P/L (brak pozycji otwartej).

US-004
Tytuł: Dodanie dywidendy
Opis: Jako użytkownik chcę dodać dywidendę (bez ilości), aby zwiększyć Realized P/L.
Kryteria akceptacji:
- Dywidenda podnosi Realized P/L o podaną kwotę.
- Rekord widoczny w tabeli z typem „dividend”.

US-005
Tytuł: Dodanie odsetek
Opis: Jako użytkownik chcę dodać odsetki (bez ilości), aby zwiększyć Realized P/L.
Kryteria akceptacji:
- Odsetki podnoszą Realized P/L o podaną kwotę.
- Rekord widoczny w tabeli z typem „interest”.

US-006
Tytuł: Aktualizacja ceny bieżącej
Opis: Jako użytkownik chcę zaktualizować ręcznie cenę bieżącą dla tickera, aby przeliczyć Unrealized P/L i Total P/L.
Kryteria akceptacji:
- Po aktualizacji ceny Unrealized P/L dla danego tickera aktualizuje się natychmiast.
- Total P/L = Realized P/L + Unrealized P/L.
- Jeśli brak ceny dla tickera, UI informuje, że Unrealized P/L nie może być policzony.

US-007
Tytuł: Filtrowanie widoku
Opis: Jako użytkownik chcę filtrować tabelę transakcji po tickerze, typie, statusie i kategorii instrumentu, aby analizować wybrane fragmenty portfela.
Kryteria akceptacji:
- Po zastosowaniu filtrów tabela pokazuje jedynie pasujące rekordy.
- KPI przeliczają się w oparciu o zakres widoku po filtrach.
- Filtry można łączyć (np. ticker=X i typ=buy).

US-008
Tytuł: Sortowanie transakcji
Opis: Jako użytkownik chcę sortować transakcje po zysku/stracie, tickerze i dacie, aby szybciej znaleźć potrzebne wpisy.
Kryteria akceptacji:
- Zmiana sortowania aktualizuje kolejność rekordów bez opóźnień.
- Sortowanie nie resetuje aktywnych filtrów.

US-009
Tytuł: Edycja transakcji w modalu
Opis: Jako użytkownik chcę edytować istniejącą transakcję w modalu i zapisać zmiany z natychmiastowym przeliczeniem KPI.
Kryteria akceptacji:
- Po zapisie edycji KPI i statusy są aktualne.
- Walidacje jak przy dodawaniu (brak ujemnych wartości, brak oversell po zmianie).
- Historia zmian nie jest przechowywana (brak śladu zmian w MVP).

US-010
Tytuł: Usunięcie transakcji (twarde)
Opis: Jako użytkownik chcę usunąć transakcję, aby skorygować błędy i natychmiast zaktualizować KPI.
Kryteria akceptacji:
- Po usunięciu dane wyliczenia (WAC, wolumen, KPI) odświeżają się.
- Usunięcie nie może pozostawić stanu niespójnego (np. sell bez buy > oversell) — jeśli tak, wyświetl komunikat i zablokuj operację.

US-011
Tytuł: Eksport CSV
Opis: Jako użytkownik chcę wyeksportować wszystkie transakcje do pliku CSV.
Kryteria akceptacji:
- Plik zapisany lokalnie z nazwą portman-transactions-YYYYMMDD-HHMM.csv.
- Kolumny co najmniej: id, data, ticker, typ, ilość, cena, kwota, waluta, kategoria, CFD, notatka.
- Dane zgodne z aktualnym stanem po filtrach (jeśli wybierzemy „eksport widoku”) lub pełny eksport (globalny) — wariant wybrany w UI.

US-012
Tytuł: Autoryzacja lokalna (pojedynczy login)
Opis: Jako użytkownik chcę zabezpieczyć dostęp do aplikacji prostym logowaniem lokalnym.
Kryteria akceptacji:
- Logowanie wymaga poprawnego loginu i hasła; hasło przechowywane jako hash.
- Po zalogowaniu sesja utrzymywana do zamknięcia aplikacji.
- Trzy nieudane próby: informacja o błędnych danych (bez ujawniania, czy login istnieje).

US-013
Tytuł: Oznaczenie CFD
Opis: Jako użytkownik chcę oznaczać transakcje jako CFD, aby odróżnić je w filtrach i analizie.
Kryteria akceptacji:
- Flaga CFD dostępna przy dodawaniu/edycji.
- Filtr „CFD” pokazuje/ukrywa odpowiednie rekordy.
- W KPI brak odrębnych reguł dla CFD w MVP (etykieta informacyjna).

US-014
Tytuł: Walidacja oversell w czasie rzeczywistym
Opis: Jako użytkownik chcę otrzymać natychmiastowy komunikat, gdy próbuję sprzedać więcej niż posiadam dla danego tickera.
Kryteria akceptacji:
- UI prezentuje komunikat z aktualnym wolumenem posiadanym.
- Zapis transakcji sell jest blokowany do czasu korekty ilości.

US-015
Tytuł: Nieskończone przewijanie w tabeli
Opis: Jako użytkownik chcę płynnie przewijać listę transakcji bez lagów do ~100 rekordów.
Kryteria akceptacji:
- Doładowywanie kolejnych rekordów nie powoduje przycięć.
- Filtry i sortowanie działają poprawnie przy przewijaniu.

US-016
Tytuł: Widok KPI zależny od filtrów
Opis: Jako użytkownik chcę, aby KPI odzwierciedlały wyłącznie dane widoczne po zastosowaniu filtrów.
Kryteria akceptacji:
- Zmiana filtrów natychmiast aktualizuje Invested, Realized, Unrealized i Total.
- Wartości procentowe liczone wg definicji MVP (Total/Invested; gdy Invested=0 → „—”).

US-017
Tytuł: Edycja z kontrolą spójności
Opis: Jako użytkownik chcę, aby edycja istniejącej transakcji nie powodowała naruszenia reguł (np. oversell) i w takim wypadku była blokowana z komunikatem.
Kryteria akceptacji:
- Zmiana buy/sell nie może doprowadzić do sell>posiadany wolumen.
- Aplikacja wskazuje minimalną wymaganą korektę ilości.

## 6. Metryki sukcesu

- Zgodność obliczeń: różnica względem arkusza Excel użytkownika ≤ ±0,01 PLN dla P/L (próby dla reprezentatywnego zestawu przypadków).
- Użyteczność: czas dodania standardowej transakcji ≤ 20 s (średnia z 5 prób).
- Poprawność danych: 0 przypadków zarejestrowanego oversell (sprzedaż > posiadany wolumen) w testach funkcjonalnych.
- Dostępność danych: pełny eksport CSV zawiera 100% transakcji widocznych w aplikacji (kontrola liczby rekordów).
- Wydajność: płynne działanie do ~100 transakcji bez zauważalnych opóźnień w interakcji (przewijanie, filtrowanie, sortowanie ≤ 200 ms odświeżenia widoku).

