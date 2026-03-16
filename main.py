import csv
import sys

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.volby.cz/pls/ps2017nss/"


def validate_arguments(arguments: list[str]) -> tuple[str, str] | None:
    """Zkontroluje vstupní argumenty programu."""
    if len(arguments) != 3:
        print("Chyba: zadej URL územního celku a název výstupního CSV souboru.")
        return None

    url = arguments[1]
    output_file = arguments[2]

    if "ps32" not in url:
        print("Chyba: první argument musí být odkaz na územní celek (ps32).")
        return None

    if not output_file.endswith(".csv"):
        print("Chyba: výstupní soubor musí mít příponu .csv.")
        return None

    return url, output_file


def download_page(url: str) -> str | None:
    """Stáhne HTML obsah stránky."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        response.encoding = "utf-8"
        return response.text
    except requests.RequestException:
        print("Chyba: stránku se nepodařilo stáhnout.")
        return None


def parse_html(html: str) -> BeautifulSoup:
    """Převede HTML text na BeautifulSoup objekt."""
    return BeautifulSoup(html, "html.parser")


def get_municipality_links(soup: BeautifulSoup) -> list[tuple[str, str]]:
    """Vrátí odkazy na detail jednotlivých obcí."""
    municipality_links = []

    for link in soup.find_all("a"):
        href = link.get("href")
        code = link.text.strip()

        if href and "ps311" in href and code.isdigit():
            municipality_links.append((code, BASE_URL + href))

    return municipality_links


def clean_text(text: str) -> str:
    """Vyčistí text od mezer."""
    return text.strip().replace("\xa0", "")


def extract_municipality_name(soup: BeautifulSoup) -> str:
    """Vrátí název obce."""
    for header in soup.find_all("h3"):
        text = header.text.strip()
        if "Obec:" in text:
            return text.replace("Obec:", "").strip()
    return "Neznámá obec"


def extract_main_data(soup: BeautifulSoup) -> dict[str, str]:
    """Vrátí základní volební údaje."""
    numbers = [clean_text(x.text) for x in soup.find_all("td", class_="cislo")]

    return {
        "voliči v seznamu": numbers[3],
        "vydané obálky": numbers[4],
        "platné hlasy": numbers[7],
    }


def extract_party_votes(soup: BeautifulSoup) -> dict[str, str]:
    """Vrátí hlasy pro jednotlivé strany."""
    votes = {}

    for row in soup.find_all("tr"):
        party = row.find("td", class_="overflow_name")
        values = row.find_all("td", class_="cislo")

        if party and len(values) >= 2:
            votes[clean_text(party.text)] = clean_text(values[1].text)

    return votes


def extract_municipality_data(code: str, url: str) -> dict[str, str] | None:
    """Vrátí kompletní data jedné obce."""
    html = download_page(url)
    if html is None:
        return None

    soup = parse_html(html)
    main_data = extract_main_data(soup)

    row = {
        "kód obce": code,
        "název obce": extract_municipality_name(soup),
        "voliči v seznamu": main_data["voliči v seznamu"],
        "vydané obálky": main_data["vydané obálky"],
        "platné hlasy": main_data["platné hlasy"],
    }

    row.update(extract_party_votes(soup))
    return row


def get_fieldnames(data: list[dict[str, str]]) -> list[str]:
    """Vrátí názvy sloupců."""
    base = [
        "kód obce",
        "název obce",
        "voliči v seznamu",
        "vydané obálky",
        "platné hlasy",
    ]

    parties = []

    for row in data:
        for key in row:
            if key not in base and key not in parties:
                parties.append(key)

    return base + parties


def save_to_csv(data: list[dict[str, str]], filename: str) -> None:
    """Uloží výsledky do CSV."""
    if not data:
        print("Chyba: žádná data.")
        return

    fieldnames = get_fieldnames(data)

    with open(filename, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def main() -> None:
    """Hlavní funkce programu."""
    validated = validate_arguments(sys.argv)
    if validated is None:
        sys.exit(1)

    url, output_file = validated

    html = download_page(url)
    if html is None:
        sys.exit(1)

    soup = parse_html(html)

    municipality_links = get_municipality_links(soup)
    if not municipality_links:
        print("Chyba: nebyly nalezeny obce.")
        sys.exit(1)

    results = []

    for code, municipality_url in municipality_links:
        data = extract_municipality_data(code, municipality_url)
        if data:
            results.append(data)

    save_to_csv(results, output_file)

    print(f"Uloženo {len(results)} obcí do souboru {output_file}")


if __name__ == "__main__":
    main()

