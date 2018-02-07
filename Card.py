import pandas as pd

class Card(object):
    cardFields = ('name',
                  'set',
                  'rarity',
                  'castingCost',
                  'cmc',
                  'rarity',
                  'oracleText',
                  'flavorText',
                  'types',
                  'subTypes',
                  'colorID',
                  'purchasePrice', #this should be entered
                  'marketPrice', #this should be private and mined from tcg
                  'investmentCost') #this should be private
    def __init__(self, *args, **kwargs):
        #inst fields

#         # Default
#         self.card_db = None
#         self.supertypes = kwargs.pop('supertypes', [])
#         self.name = kwargs.pop('name', '')
#         self.subtypes = kwargs.pop('subtypes', [])
#         self.text = kwargs.pop('text', r'')
#         self.colorid = kwargs.pop('colorid', r'')
#         self.power = kwargs.pop('power', np.nan)
#         self.toughness = kwargs.pop('toughness', np.nan)
#         self.cmc = kwargs.pop('cmc', 0)
#         self.mana_cost = kwargs.pop('mana_cost', r'')
#         self.flavor_text = kwargs.pop('flavor_text', '')

        fields_seen = []
        self._info = pd.DataFrame()
        for kw, val in kwargs.items():
            if kw in  Card.cardFields:
                setattr(self, kw, val)
                fields_seen.append(kw)
            else:
                print('{keyword} not recognized, ignoring!'.format(keyword=kw))
        for arg in args:
            print('{arg} not supported, ignoring!'.format(arg=arg))
        for field in Card.cardFields:
            if field not in fields_seen:
                setattr(self, field, None)
        #set fields to pandas
        self.set_card_info()

    def set_card_info(self):
        pd.DataFrame({field:self.field for field in Card.cardFields})

    def get_card_info(self):
        return self._info

    def __getattr__(self, name):
        return self._info.__getattribute__(name)

    # def __repr__(self):
        # return self.name
