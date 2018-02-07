def generateBasicLands(type='generator'):
    basics = ('Plains', 'Island', 'Swamp','Mountain', 'Forest')
    short = ('w', 'u', 'b','r', 'g')
    if 'generator' in type:
        for basic in basics:
            yield basic
    elif 'list' in type:
        return basics
    elif 'dict' in type:
        return dict(zip(short, basics))

def sumCards(mtgCardList, **kwargs):
    import pandas as pd
    kwargs.setdefault('cardName', 'CardName')
    kwargs.setdefault('quantName', 'Quantitiy')
    #Check for CardName and Quantity
    def checkForColumn(colName, alternate):
        if colName in mtgCardList.columns:
            nameCall = colName
        else:
            for col in mtgCardList.columns:
                if alternate in col.lower():
                    nameCall = col
                    break
                else:
                    nameCall = None
        if nameCall is None:
            raise Exception(" ".join(['Cannot Find "{colName}" column:',
                    'Either place "{alternate}" in column name or call column',
                    '"{colName}"']).format(colName=colName,
                                           alternate=alternate))
        return nameCall
    nameCall = checkForColumn(kwargs['cardName'], 'name')
    quantCall = checkForColumn(kwargs['quantName'], 'quant')
    seenCards = []
    newCardDict = {}
    for card in mtgCardList[nameCall]:
        if card not in seenCards:
            seenCards.append(card)
            newCardDict[card] = mtgCardList[quantCall]
        else:
            newCardDict[card] += mtgCardList[quantCall]
    return pd.DataFrame([(quant, name) for name, quant in newCardDict.items()],
                        columns=[quantCall, nameCall])

