from posgram_finder import PosgramFinder
from pprint import pprint

p = PosgramFinder()
result = p.posgram_errors("Seal palju kohvikuid, muuseume, kino. Ma lähen ujuma meres ja matkama!")
pprint(result, sort_dicts=False)
