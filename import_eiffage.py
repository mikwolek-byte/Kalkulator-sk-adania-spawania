"""Import explicit tables, never infer welds from a BOM or a profile name."""
import io
from openpyxl import load_workbook

def load_rows(raw):
    w = load_workbook(io.BytesIO(raw), data_only=True, read_only=True)
    try:
        if 'Czasy' not in w: raise ValueError('Brak arkusza Czasy')
        # Only costing columns. Scheduling grids are intentionally not imported.
        rows = list(w['Czasy'].iter_rows(max_col=15, values_only=True))
        return rows
    finally: w.close()

def transport(mass, welding=False):
    bands = [(12000.9,45),(3000.9,35),(1500.9,25),(500.9,15),(300.9,10),(150.9,7),(50.9,5),(0,4)] if welding else [(12000.9,90),(3000.9,60),(1500.9,50),(500.9,30),(300.9,20),(100.9,15),(0,4)]
    return next((minutes for threshold,minutes in bands if mass > threshold), 0)

def numeric(value, label, default=None):
    if value is None and default is not None: return default
    if not isinstance(value, (int,float)): raise ValueError('Brak wartości obliczonej w Excelu: ' + label + '. Przelicz i zapisz skoroszyt w Excelu.')
    return value

def assembly_import(raw):
    rows = load_rows(raw); elements=[]; items=[]; current=None
    for idx,row in enumerate(rows):
        b,c,d = row[1:4]
        if idx+1 < len(rows) and rows[idx+1][1:4] == ('Profil','Ilość','Fazowanie') and b not in (None,0,'0'):
            mass=numeric(d, f'Czasy!D{idx+1}')
            current=str(b).strip()
            if any(e['element']==current for e in elements): raise ValueError('Powtórzony blok: '+current)
            elements.append(dict(element=current,sztuk=1,masa_kg=mass,transport_skladanie_min=transport(mass),transport_spawanie_min=transport(mass,True)))
            continue
        if not current or not b or b in ['Profil','Transport','SUMA']: continue
        if not isinstance(c,(int,float)) or c<=0: continue
        base_rate=numeric(row[7],f'Czasy!H{idx+1}',0)
        text=str(b).strip(); kind='blacha' if text.lower().startswith('blacha') else 'profil główny' if base_rate==20 else 'profil dodatkowy'
        items.append(dict(element=current,pozycja=text,rodzaj=kind,sztuk=c,fazowanie_mm=numeric(d,'fazowanie',0),fazowanie_min_m=numeric(row[4],'norma fazowania',0),klinkowanie_mm=numeric(row[5],'klinkowanie',0),klinkowanie_min_m=numeric(row[6],'norma klinkowania',0),dodatek_min=numeric(row[10],'dodatek',0),zatwierdzone=False,zrodlo=f'Składanie/Czasy!B{idx+1}:L{idx+1}'))
    if not elements: raise ValueError('Nie rozpoznano bloków Eiffage składanie')
    return elements,items

def welding_import(raw):
    rows=load_rows(raw);current=None;items=[]
    for idx,row in enumerate(rows):
        if idx+1<len(rows) and rows[idx+1][1:4]==('Pozycja','Ilość','Profil') and row[1] not in (None,0,'0'):
            current=str(row[1]).strip();continue
        if not current or row[1] in (None,'Pozycja') or not isinstance(row[2],(int,float)) or row[2]<=0:continue
        qty=row[2]; heating=numeric(row[12],'grzanie',0)/1000
        dimensions=[(row[6],row[8]),(row[7],row[9]),(row[10],row[11])]
        used=False
        for axis,(length,mult) in enumerate(dimensions):
            if mult in (None,0): continue  # no weld along this dimension in the source
            length=numeric(length,f'Czasy długość, wiersz {idx+1}')/1000
            items.append(dict(element=current,pozycja=str(row[1]).strip()+f' / kierunek {axis+1}',dlugosc_m=length,powtorzenia=qty,mnoznik_przejsc=numeric(mult,'mnożnik przejść'),grzanie_m=heating if not used else 0,wylaczona=False,zatwierdzone=False,zrodlo=f'Spawanie/Czasy!B{idx+1}:O{idx+1}'))
            used=True
    if not items: raise ValueError('Nie rozpoznano obmiaru spawania')
    return items

def import_pair(assembly_bytes,welding_bytes):
    elements,assembly=assembly_import(assembly_bytes);welds=welding_import(welding_bytes)
    if {e['element'] for e in elements}!={r['element'] for r in welds}:raise ValueError('Różne elementy w obu plikach')
    w=load_workbook(io.BytesIO(assembly_bytes),data_only=True,read_only=True)
    try:
        if 'Zakres' not in w: raise ValueError('Brak zestawienia elementów Zakres')
        meta={str(r[1]).strip(): r for r in w['Zakres'].iter_rows(min_row=6,max_row=407,max_col=9,values_only=True) if r[1] not in (None,0)}
        for e in elements:
            if e['element'] not in meta:raise ValueError('Brak liczby elementów: '+e['element'])
            e['sztuk']=numeric(meta[e['element']][5],'liczba elementów')
    finally:w.close()
    return dict(version=1,elements=elements,assembly=assembly,welds=welds)
