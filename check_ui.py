"""UI smoke check executed on the Windows build runner."""
from streamlit.testing.v1 import AppTest
app=AppTest.from_file('app.py').run(timeout=40)
assert not app.exception, str(app.exception)
next(b for b in app.button if b.label=='Zatwierdź wszystkie widoczne pozycje obmiaru').click()
app.run(timeout=40)
assert not app.exception,str(app.exception)
assert len(app.metric)==4
assert app.metric[0].value=='0.67',app.metric[0].value
assert app.metric[1].value=='0.50',app.metric[1].value
print('UI OK: zatwierdzanie i wyniki składania/spawania')
