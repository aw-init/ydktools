"""Holds datatype for yugioh cards"""
import collections
from . import banlist
class YugiohCard(object):
	""" holds all the data of a single yugioh card.
	
	:ivar name: full name of the card
	:vartype name: unicode
	
	:ivar text: text on the card
	:vartype text: unicode
	
	:ivar category: a text string that says what kind of card it is (i.e. Normal Spell, Counter Trap, Synchro Monster, etc)
	:vartype category: string
	
	:ivar cid: the unique card id
	:vartype cid: string
	
	:ivar attribute: the attribute of the monster
	:vartype attribute: string
	
	:ivar type: the type of the monster
	:vartype type: string
	
	:ivar level: the level/rank of the monster
	:vartype level: int
	
	:ivar attack: the attack stat of the monster. ? attack is negative
	:vartype attack: int
	
	:ivar defense: the defense stat of the monster. ? defense is negative
	:vartype defense: int
	
	:ivar left_scale: The left pendulum scale of the monster
	:vartype left_scale: int
	
	:ivar right_scale: The right pendulum scale of the monster
	:vartype right_scale: int
	"""
	banlist_cache = banlist.load_banlists()
	
	def __init__(self, name, text, cid, category, attribute, race, attack, defense, level, lscale=None, rscale=None, banlist_data = None):
		self.name = name.encode('utf8', 'replace')
		self.uname = name
		
		self.text = text.encode('utf8', 'replace')
		self.utext = text
		
		self.category = category
		
		self.cid = cid		
		
				
		# only exist for monsters
		self.attribute = attribute if attribute != "N/A" else None
		
		self.type = race if race != "N/A" else None
		
		self.level = level
		
		self.attack = attack
		
		self.defense = defense
		
		self.left_scale = lscale
		
		self.right_scale = rscale		
		
		self._banlist_status = {}
		
		
		if banlist_data:
			for name, count in banlist_data:
				self._banlist_status[name] = count
		else:
			for BL in YugiohCard.banlist_cache:
				self._banlist_status[BL.name] = BL.allowed(self.name, self.text)

		
	def __hash__(self):
		return hash(self.cid)
	def __eq__(self, other):
		return isinstance(other, YugiohCard) and self.cid == other.cid
		
	def __lt__(self, other):
		return self.cid < other.cid
	def __gt__(self, other):
		return self.cid > other.cid
		
	def __iter__(self):
		return iter(self.as_dict().items())
	def __getitem__(self, key):
		return self.as_dict()[key]
		
	def __repr__(self):
		return 'YugiohCard({0})'.format(str(self))
	def __str__(self):
		return self.name
		
	def description(self):
		"""Return a formatted string depiction of the card, matching the format of a physical card as much as possible.
		
		:returns: A string describing the card.
		:rtype: string"""
		output = '{0} ({1})\n'.format(self.name, self.cid)
		if self.is_monster():
			output += '{0} {1}\n'.format(self.attribute, '*' * self.level)
			output += self._type_line() + '\n'
			output += 'ATK {0}'.format(self.attack if self.attack >= 0 else '?')
			output += ' / DEF {0}\n'.format(self.defense if self.defense >= 0 else '?')
		else:		
			output += self._type_line() + '\n'
		output += '{0}\n'.format(self.text)
		return output
		
	def _type_line(self):
		if self.is_monster():
			types = [self.type]
			parts = self.category.split('-')[:-1]
			types.extend(parts)
			return '/'.join(types)
		else:
			return ' '.join(self.category.split('-'))
		
	def as_dict(self):
		"""Get the card data as a python dict, for conversion to json.
		
		:returns: the card as a dict.
		:rtype: dict"""
		return {
			'name' : self.name,
			'text' : self.text,
			'category' : self.category,
			'cid' : self.cid,
			'type' : self.type,
			'attribute' : self.attribute,
			'level' : self.level,
			'attack' : self.attack,
			'defense' : self.defense,
			'left_scale' : self.left_scale,
			'right_scale' : self.right_scale,
			'banlist' : self._banlist_status
		}
			
		
	def get(self, key):
		"""Get attribute of the card by string instead of direct indexing. Mostly used internally. Roughly equivalent to getattr(obj, attr)
		
		:param key: the name of the attribute to get.
		:type key: string
		:returns: information about the card."""
		return self.as_dict()[key]
		
	def is_monster(self):
		"""
		:returns: True if card is a monster card
		:rtype: boolean"""
		return 'Monster' in self.category
		
	def is_spell(self):
		"""
		:returns: True if card is a spell card
		:rtype: boolean"""
		return 'Spell' in self.category
		
	def is_trap(self):
		"""
		:returns: True if card is a trap card
		:rtype: boolean"""
		# damn son, where'd you find this?
		return 'Trap' in self.category
		
	def is_pendulum(self):
		"""
		:returns: True if card is a pendulum card
		:rtype: boolean"""
		return 'Pendulum' in self.category
		
	def is_synchro(self):
		"""
		:returns: True if card is a synchro card
		:rtype: boolean"""
		return 'Synchro' in self.category
		
	def is_xyz(self):
		"""
		:returns: True if card is an xyz card
		:rtype: boolean"""
		return 'Xyz' in self.category
		
	def is_fusion(self):
		"""
		:returns: True if card is an xyz card
		:rtype: boolean"""
		return 'Fusion' in self.category
		
	def is_tuner(self):
		"""
		:returns: True if card is a tuner card
		:rtype: boolean"""
		return 'Tuner' in self.category
		
	def is_effect_monster(self):
		"""
		:returns: True if card is an effect monster card
		:rtype: boolean"""
		return 'Effect' in self.category
		
	def is_normal_monster(self):
		"""
		:returns: True if card is a monster card. This is not the same as a monster without an effect.
		:rtype: boolean """
		return self.category in ['Normal-Monster', 'Token']
		
	def is_ritual_monster(self):
		"""
		:returns: True if card is a Ritual monster card
		:rtype: boolean"""
		return self.is_monster and 'Ritual' in self.category
		
	def is_extra_deck(self):
		return self.is_xyz() or self.is_fusion() or self.is_synchro()
	def is_main_deck(self):
		return not self.is_extra_deck()

	def allowed(self, banlist='TCG'):
		"""
		:param banlist: what banlist you are asking about.
		:type banlist: string
		:returns: How many copies are allowed on the given banlist.
		:rtype: int"""
		for key in self._banlist_status:
			if banlist.upper() in key:
				return self._banlist_status[key]
		raise KeyError('No banlist called {0}'.format(banlist))