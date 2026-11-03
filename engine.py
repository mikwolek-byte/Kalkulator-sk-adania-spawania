"""Deterministic calculation core. All input times are net minutes."""
from dataclasses import dataclass, asdict
import math

ASSEMBLY_RATES = {'blacha': 10.0, 'profil dodatkowy': 15.0, 'profil główny': 20.0}

@dataclass(frozen=True)
class Settings:
    welding_min_m: float = 8.0
    assembly_factor: float = 2.0
    welding_factor: float = 2.5
    round_rows: bool = False
    include_extras: bool = False
    heating_min_m: float = 5.0

def number(value, name, positive=False, integer=False):
    if isinstance(value, bool): raise ValueError(f'{name}: oczekiwana liczba')
    try: value = float(value)
    except (TypeError, ValueError): raise ValueError(f'{name}: brak liczby')
    if not math.isfinite(value) or value < 0 or (positive and value == 0):
        raise ValueError(f'{name}: nieprawidłowa wartość {value}')
    if integer and value != int(value): raise ValueError(f'{name}: wymagana liczba całkowita')
    return value

def up(value, enabled):
    # Eliminate binary artifacts immediately above an integer minute.
    return math.ceil(round(value, 10)) if enabled else value

def validate_project(project):
    if not isinstance(project, dict): raise ValueError('Nieprawidłowy projekt')
    ids = []
    for item in project.get('elements', []):
        key = str(item.get('element', '')).strip()
        if not key or key in ids: raise ValueError('Puste lub powtórzone oznaczenie elementu')
        ids.append(key)
        number(item.get('sztuk'), key + ' / sztuki', positive=True, integer=True)
        number(item.get('masa_kg'), key + ' / masa', positive=True)
    if not ids: raise ValueError('Brak elementów wysyłkowych')
    for section in ['assembly', 'welds']:
        if not project.get(section): raise ValueError('Brak danych: ' + section)
        for row in project[section]:
            if row.get('element') not in ids: raise ValueError('Nieznany element w ' + section)
            if row.get('zatwierdzone') is not True:
                raise ValueError('Zatwierdź obmiar: ' + str(row.get('pozycja', '')))
    for key in ids:
        if not any(r['element'] == key for r in project['assembly']): raise ValueError(key + ': brak składania')
        if not any(r['element'] == key for r in project['welds']): raise ValueError(key + ': brak obmiaru spoin')

def calculate(project, settings=Settings()):
    validate_project(project)
    for name, value in asdict(settings).items():
        if name not in ['round_rows', 'include_extras']: number(value, name, positive=True)
    assembly, welds, summary = [], [], []
    for row in project['assembly']:
        kind = row['rodzaj']
        if kind not in ASSEMBLY_RATES: raise ValueError('Wybierz rodzaj detalu: ' + str(kind))
        qty = number(row['sztuk'], 'Liczba detali', positive=True, integer=True)
        net = qty * ASSEMBLY_RATES[kind]
        extra = 0.0
        if settings.include_extras:
            extra = qty * (number(row.get('fazowanie_mm', 0), 'Fazowanie') * number(row.get('fazowanie_min_m', 0), 'Norma fazowania') + number(row.get('klinkowanie_mm', 0), 'Klinkowanie') * number(row.get('klinkowanie_min_m', 0), 'Norma klinkowania')) / 1000 + number(row.get('dodatek_min', 0), 'Dodatek')
        assembly.append({**row, 'netto_min': up(net + extra, settings.round_rows)})
    for row in project['welds']:
        if row.get('wylaczona', False):
            welds.append({**row, 'metry_przejsc': 0.0, 'netto_min': 0.0}); continue
        length = number(row['dlugosc_m'], 'Długość spoiny', positive=True)
        qty = number(row['powtorzenia'], 'Powtórzenia', positive=True, integer=True)
        multiplier = number(row['mnoznik_przejsc'], 'Ściegi × odcinki', positive=True, integer=True)
        metres = length * qty * multiplier
        heating = number(row.get('grzanie_m', 0), 'Długość grzania') * qty if settings.include_extras else 0.0
        welds.append({**row, 'metry_przejsc': metres, 'netto_min': up(metres * settings.welding_min_m + heating * settings.heating_min_m, settings.round_rows)})
    for item in project['elements']:
        key = item['element']; qty = float(item['sztuk']); mass = float(item['masa_kg']) * qty
        a = sum(r['netto_min'] for r in assembly if r['element'] == key)
        w = sum(r['netto_min'] for r in welds if r['element'] == key)
        if settings.include_extras:
            a += number(item.get('transport_skladanie_min', 0), 'Transport składanie')
            w += number(item.get('transport_spawanie_min', 0), 'Transport spawanie')
        ah = a * qty * settings.assembly_factor / 60
        wh = w * qty * settings.welding_factor / 60
        summary.append({'element': key, 'sztuk': qty, 'masa_kg': mass, 'skladanie_netto_min_szt': a, 'spawanie_netto_min_szt': w, 'skladanie_rbg': ah, 'spawanie_rbg': wh, 'suma_rbg': ah + wh, 'rbg_t': (ah + wh) / (mass / 1000)})
    total_mass = sum(r['masa_kg'] for r in summary)
    totals = {k: sum(r[k] for r in summary) for k in ['skladanie_rbg', 'spawanie_rbg', 'suma_rbg']}
    totals.update(masa_kg=total_mass, rbg_t=totals['suma_rbg'] / (total_mass / 1000))
    return {'summary': summary, 'totals': totals, 'assembly': assembly, 'welds': welds, 'settings': asdict(settings)}
