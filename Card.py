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
        fieldsSeen = []
        self._info = pd.DataFrame()
        for kw, val in kwargs.items():
            if kw in  Card.cardFields:
                setattr(self, kw, val)
                fieldsSeen.append(kw)
            else:
                print('{keyword} not recognized, ignoring!'.format(keyword=kw))
        for arg in args:
            print('{arg} not supported, ignoring!'.format(arg=arg))
        for field in Card.cardFields:
            if field not in fieldsSeen:
                setattr(self, field, None)
        #set fields to pandas
        self.setCardInfo()

    def setCardInfo(self):
        pd.DataFrame({field:self.field for field in Card.cardFields})

    def getCardInfo(self):
        return self._info

    def __getattr__(self, name):
        return self._info.__getattribute__(name)

    # def __repr__(self):
        # return self.name
