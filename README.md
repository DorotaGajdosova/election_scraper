# Elections Scraper

Python projekt pro scrapování výsledků voleb z webu volby.cz.

## Popis projektu

Skript stáhne výsledky hlasování pro všechny obce z vybraného územního celku a uloží je do CSV souboru.

Výstup obsahuje:

- kód obce
- název obce
- voliči v seznamu
- vydané obálky
- platné hlasy
- hlasy pro jednotlivé kandidující strany

## Instalace

Nejprve vytvoř virtuální prostředí:

python -m venv venv

Aktivace ve Windows:

venv\Scripts\activate

Nainstaluj potřebné knihovny:

pip install -r requirements.txt

## Spuštění programu

Program se spouští se dvěma argumenty:

py .\main.py "URL_UZEMNIHO_CELKU" vystup.csv

Příklad:

py .\main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=1&xnumnuts=1100" vysledky.csv

## Výstup

Program vytvoří CSV soubor obsahující výsledky hlasování pro všechny obce ve zvoleném územním celku.

## Použité knihovny

- requests
- beautifulsoup4