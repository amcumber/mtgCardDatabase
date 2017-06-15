import pandas as pd
import pickle
# import datetime #add datetime to saveDb to default a unique val

#TODO ########
# init
# instantiate cards into card objs
# move card obj into a pandas view
# How do you organize this card obj and a pandas view??

class CardDB(object):
    def __init__(self, *args, **kwargs):
        self._info = pd.DataFrame()
        for card in kwargs.setdefault('cardList', []):
            self.addCard(card)

    def getInformation(self):
        pass

    def saveDB(self, *args, **kwargs):
        kwargs.setdefault('fileType', 'pickle')
        kwargs.setdefault('fileName', './cardDB') #add datetime
        if 'pickle' in kwargs['filetype'].lower():
            return self.saveDBasPickle(kwargs['fileName'])
        elif 'csv' in kwargs['filetype'].lower():
            return self.saveDBasCSV(kwargs['fileName'])
        if 'xls' in kwargs['filetype'].lower():
            return self.saveDBasXLS(kwargs['fileName'])

    def loadDB(self, fileName, *args, **kwargs):
        kwargs.setdefault('fileType', 'pickle')
        if 'pickle' in kwargs['filetype'].lower():
            return self.saveDBasPickle(fileName)
        elif 'csv' in kwargs['filetype'].lower():
            return self.saveDBasCSV(fileName)
        if 'xls' in kwargs['filetype'].lower():
            return self.saveDBasXLS(fileName)

    def saveDBasPickle(self, fileName):
        pickle.dump(self, fileName)

    def saveDBasCSV(self, fileName):
        pass

    def saveDBasXLS(self, fileName):
        pass

    def loadPickleasDB(self, fileName):
        pickle.load(fileName)

    def loadCSVasDB(self, fileName):
        pass

    def loadXLSasDB(self, fileName):
        pass

    def addCard(self, cardObj):
        self.cardList.append(cardObj)
        self._info.combineAdd(cardObj.getCardInfo)
