import json
from dataclasses import asdict
import pandas as pd
import streamlit as st
from engine import calculate, Settings
from import_eiffage import import_pair

st.set_page_config(page_title='Zekon — kalkulator czasu',layout='wide')
st.title('Kalkulator czasu warsztatowego')
st.caption('Składanie i spawanie • czasy netto, współczynniki i rbg/t')

def fresh():
    return {'version':1,'elements':[dict(element='E-1',sztuk=1,masa_kg=1000,transport_skladanie_min=0,transport_spawanie_min=0)],
        'assembly':[dict(element='E-1',pozycja='Profil główny',rodzaj='profil główny',sztuk=1,zatwierdzone=False,zrodlo='Wpis ręczny')],
        'welds':[dict(element='E-1',pozycja='Spoina 1',dlugosc_m=0.5,powtorzenia=1,mnoznik_przejsc=3,grzanie_m=0,wylaczona=False,zatwierdzone=False,zrodlo='Wpis ręczny')]}

if 'project' not in st.session_state:st.session_state.project=fresh()
if 'revision' not in st.session_state:st.session_state.revision=0
def set_project(p):
    for key in ['elements','assembly','welds']:
        if not isinstance(p.get(key),list):raise ValueError('Brak tabeli '+key)
    st.session_state.project=p;st.session_state.revision+=1

with st.expander('Wczytaj projekt lub pliki Eiffage',expanded=True):
    mode=st.radio('Źródło',['Projekt JSON','Para Excel Eiffage'],horizontal=True)
    if mode=='Projekt JSON':
        uploaded=st.file_uploader('Projekt',type=['json'])
        if st.button('Wczytaj projekt',disabled=uploaded is None):
            try:set_project(json.loads(uploaded.getvalue()));st.rerun()
            except Exception as exc:st.error(str(exc))
    else:
        left,right=st.columns(2)
        a=left.file_uploader('Excel — składanie',type=['xlsx'])
        w=right.file_uploader('Excel — spawanie',type=['xlsx'])
        st.info('Importujemy tabele Czasy i ilości z Zakres. Ręczne wyniki zbiorcze oraz korekty ×4 są pomijane. Po imporcie zatwierdź obmiar i klasyfikację detali. Dane muszą być przeliczone i zapisane w Excelu.')
        if st.button('Importuj Excel',disabled=a is None or w is None):
            try:set_project(import_pair(a.getvalue(),w.getvalue()));st.rerun()
            except Exception as exc:st.error(str(exc))

p=st.session_state.project
defaults=p.get('settings',{})
rev=st.session_state.revision
with st.sidebar:
    st.header('Normy netto')
    st.write('Blacha: **10 min/szt.**\n\nProfil dodatkowy: **15 min/szt.**\n\nProfil główny: **20 min/szt.**')
    rate=st.number_input('Spawanie [min/mb/ścieg]',min_value=0.01,value=float(defaults.get('welding_min_m',8)),key=f'rate{rev}')
    fa=st.number_input('Współczynnik składania',min_value=0.01,value=float(defaults.get('assembly_factor',2)),key=f'fa{rev}')
    fw=st.number_input('Współczynnik spawania',min_value=0.01,value=float(defaults.get('welding_factor',2.5)),key=f'fw{rev}')
    extras=st.checkbox('Uwzględnij dodatki z Excela',value=bool(defaults.get('include_extras',False)),key=f'ex{rev}')
    st.caption('Dodatki: fazowanie, klinkowanie, transport wewnętrzny oraz grzanie 5 min/m. Domyślnie wyłączone. Normy szczegółowe składania pozostają 10/15/20.')
    st.caption('Brak minimum 1 mb. Wszystkie współczynniki stosowane jeden raz, po zsumowaniu czasów netto.')
    if st.button('Nowy pusty projekt'):set_project(fresh());st.rerun()

st.subheader('1. Elementy wysyłkowe')
st.caption('Masa jednostkowa w kg. Ilości detali i obmiar spoin poniżej dotyczą jednej sztuki elementu wysyłkowego.')
elements=st.data_editor(pd.DataFrame(p['elements']),num_rows='dynamic',key=f'e{rev}',hide_index=True)
st.subheader('2. Składanie')
assembly=st.data_editor(pd.DataFrame(p['assembly']),num_rows='dynamic',key=f'a{rev}',hide_index=True,column_config={'rodzaj':st.column_config.SelectboxColumn('Rodzaj detalu',options=['blacha','profil dodatkowy','profil główny'],required=True),'zatwierdzone':st.column_config.CheckboxColumn('Zatwierdzone')})
st.subheader('3. Spawanie')
st.caption('Mnożnik przejść = liczba jednakowych odcinków × liczba ściegów. Przykład: 2 strony × 3 ściegi = 6. Przy imporcie Eiffage zachowuje wartości I/J/L, bez ponownego mnożenia ich przez ściegi.')
st.caption('Import Excela nie rozpoznaje automatycznie typu ani grubości spoin. Wpisz lub sprawdź mnożniki według zatwierdzonej tabeli technologicznej. Spoiny wzdłużne IKS wyłącz przez pole „wylaczona”.')
welds=st.data_editor(pd.DataFrame(p['welds']),num_rows='dynamic',key=f'w{rev}',hide_index=True,column_config={'zatwierdzone':st.column_config.CheckboxColumn('Zatwierdzone'),'wylaczona':st.column_config.CheckboxColumn('Wyłączona')})
def records(frame):return json.loads(frame.to_json(orient='records',force_ascii=False))
current={'version':1,'elements':records(elements),'assembly':records(assembly),'welds':records(welds)}
if st.button('Zatwierdź wszystkie widoczne pozycje obmiaru'):
    for section in ['assembly','welds']:
        for r in current[section]:r['zatwierdzone']=True
    current['settings']={'welding_min_m':rate,'assembly_factor':fa,'welding_factor':fw,'include_extras':extras}
    set_project(current);st.rerun()

cfg=Settings(welding_min_m=rate,assembly_factor=fa,welding_factor=fw,include_extras=extras)
saved={**current,'settings':asdict(cfg)}
st.download_button('Zapisz projekt JSON',json.dumps(saved,ensure_ascii=False,indent=2),file_name='projekt_zekon.json',mime='application/json')
try:
    result=calculate(current,cfg);t=result['totals']
    st.subheader('Wynik')
    c1,c2,c3,c4=st.columns(4)
    for col,label,key in [(c1,'Składanie [rbg]','skladanie_rbg'),(c2,'Spawanie [rbg]','spawanie_rbg'),(c3,'Suma [rbg]','suma_rbg'),(c4,'Łącznie [rbg/t]','rbg_t')]:col.metric(label,f'{t[key]:.2f}')
    summary=pd.DataFrame(result['summary']);st.dataframe(summary,hide_index=True)
    st.download_button('Pobierz wynik CSV',summary.to_csv(index=False,sep=';',decimal=',').encode('utf-8-sig'),file_name='czas_warsztatowy.csv',mime='text/csv')
    st.download_button('Pobierz pełny raport JSON',json.dumps(result,ensure_ascii=False,indent=2),file_name='raport_zekon.json',mime='application/json')
except (ValueError,KeyError,TypeError) as exc:
    st.warning('Wynik niedostępny: '+str(exc))
