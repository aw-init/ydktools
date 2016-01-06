from .core import yugiohprices, card, deck
from . import search

class CardRelease(object):
	def __init__(self, print_tag, set_name, rarity, price_data):
		self.print_tag = print_tag
		self.set_name = set_name
		self.rarity = rarity
		if price_data:
			self.has_price = True
			self.low = price_data['low']
			self.high = price_data['high']
			self.average = price_data['average']
			self.delta = price_data['shift']
		else:
			self.has_price = False
			self.low = None
			self.high = None
			self.average = None
			self.delta = None
	def __hash__(self):
		return hash(self.print_tag)
	def __eq__(self, other):
		return isinstance(other, CardRelease) and self.print_tag == other.print_tag
	def is_holo(self):
		return self.rarity not in ('Common', 'Rare', 'Short Print')
	def hype(self):
		return self.delta[1]
		
def rarity_score(release):
	if isinstance(release, CardRelease):
		rarity = release.rarity
	else:
		rarity = release
	rarity_order = [
		'Common',
		'Short Print',
		'Rare',
		'Super Rare',
		'Super Short Print',
		'Secret Rare',
		'Parallel Rare',
		'Holofoil Rare',
		'Ultra Rare',
		'Gold Ultra Rare',
		'Ultra Secret Rare',
		'Secret Ultra Rare',
		'Prismatic Secret Rare',
		'Ultimate Rare',
		'Ghost Rare'
	]
	score = 1
	for sample in rarity_order:
		if rarity.replace(' ','').lower() in sample.replace(' ','').lower():
			return 10*score # big numbers are cool
		score += 1
	return 15
	
def _rarity_at_least(x, y):
	'''Return if the rarity of y is better than the rarity of x'''
	return rarity_score(x) >= rarity_score(y)
			
class ReleaseSet(object):
	def __init__(self, card, versions):
		self.card = card
		self._versions = set(versions)
		self.has_price = any(x.has_price for x in self._versions)
	def __iter__(self):
		return iter(self._versions)
	def __len__(self):
		return len(self._versions)
	def holos(self):
		return ReleaseSet(self.card, (x for x in self._versions if x.is_holo()))
	def select(self, f):
		return ReleaseSet(self.card, (x for x in self._versions if f(x)))
	def select_at_least(self, rarity):
		baseline = rarity_score(rarity)
		def better_than_baseline(version):
			return rarity_score(version) >= baseline
		return self.select(better_than_baseline)
	def select_max_rarity(self, rarity):
		if len(self) > 0:
			def sortkey(version):
				return _pick_rarity(version.rarity)
			versions = sorted(list(self._versions), key=sortkey)
			return ReleaseSet(self.card, [versions[0]])
		else:
			return ReleaseSet(self.card, [])
	def price_sort(self, key='low'):
		if key == 'low':
			return list(sorted(self._versions, key=lambda x: x.low))
		elif key == 'high':
			return list(sorted(self._versions, key=lambda x: x.high))
		elif key == 'average':
			return list(sorted(self._versions, key=lambda x: x.average))
		elif key == 'average':
			return list(sorted(self._versions, key=lambda x: x.average))
		elif key == 'hype':
			return list(sorted(self._versions, key=lambda x: x.hype()))
		else:
			return list(sorted(self._versions, key=f))
	def cheapest_release(self):
		if self.has_price:
			return min((x.low, x) for x in self if x.has_price)[1]
	def price(self):
		if self.has_price:
			return min(x.low for x in self if x.has_price)
		else:
			return None

def card_versions(card_key, fail=False):
	card = search.find(card_key)
	if fail:
		all_data = yugiohprices.get_card_prices(card.name.encode('utf8', 'replace'))
	else:
		try:
			all_data = yugiohprices.get_card_prices(card.name.encode('utf8', 'replace'))
		except yugiohprices.APIError:
			return ReleaseSet(card, [])
	results = []
	for dat in all_data:
		results.append(CardRelease(
			dat['print_tag'],
			dat['set_name'],
			dat['rarity'],
			dat['price_data']))
	return ReleaseSet(card, results)

def card_sets():
	return yugiohprices.card_sets()

def card_support(card_key):
	card = search.find(card_key)
	support = yugiohprices.card_support(card.name.encode('utf8', 'replace'))
	result = []
	for name in support:
		result.append(search.find(name))
	return deck.YugiohSet(result)