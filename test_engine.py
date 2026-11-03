import copy
import unittest
from engine import calculate, Settings

def sample():
    return {'elements':[{'element':'A','sztuk':2,'masa_kg':1000}],
      'assembly':[{'element':'A','pozycja':'blachy','rodzaj':'blacha','sztuk':3,'zatwierdzone':True},{'element':'A','pozycja':'profil','rodzaj':'profil główny','sztuk':1,'zatwierdzone':True}],
      'welds':[{'element':'A','pozycja':'W1','dlugosc_m':0.4,'powtorzenia':2,'mnoznik_przejsc':3,'zatwierdzone':True}]}

class EngineTests(unittest.TestCase):
    def test_units_quantity_and_single_factors(self):
        r=calculate(sample());self.assertAlmostEqual(r['totals']['skladanie_rbg'],50*2*2/60)
        self.assertAlmostEqual(r['totals']['spawanie_rbg'],.4*2*3*8*2.5*2/60)
        self.assertAlmostEqual(r['totals']['rbg_t'],r['totals']['suma_rbg']/2)
    def test_no_one_metre_floor(self):
        p=sample();p['welds'][0]['dlugosc_m']=.1
        self.assertAlmostEqual(calculate(p)['totals']['spawanie_rbg'],calculate(sample())['totals']['spawanie_rbg']/4)
    def test_missing_data_blocks_result(self):
        for key in ['dlugosc_m','powtorzenia','mnoznik_przejsc']:
            p=sample();p['welds'][0][key]=None
            with self.assertRaises(ValueError):calculate(p)
    def test_unreviewed_blocks(self):
        p=sample();p['assembly'][0]['zatwierdzone']=False
        with self.assertRaises(ValueError):calculate(p)
    def test_nan_and_negative(self):
        for value in [float('nan'),float('inf'),-1,0]:
            p=sample();p['elements'][0]['masa_kg']=value
            with self.assertRaises(ValueError):calculate(p)
    def test_excluded_welds(self):
        p=sample();p['welds'][0]['wylaczona']=True
        self.assertEqual(calculate(p)['totals']['spawanie_rbg'],0)
    def test_no_mutation(self):
        p=sample();q=copy.deepcopy(p);calculate(p);self.assertEqual(p,q)
    def test_optional_extras(self):
        p=sample();p['welds'][0]['grzanie_m']=1
        self.assertAlmostEqual(calculate(p,Settings(include_extras=True))['totals']['spawanie_rbg']-calculate(p)['totals']['spawanie_rbg'],1*2*5*2.5*2/60)

if __name__=='__main__':unittest.main()
