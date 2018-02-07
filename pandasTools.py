import pandas as pd
def readTCGStylecsv(path, **kwargs):
    """
    Read a TCG style csv: quantitiy, card name, sideboard
    """
    colNames = ('Quantity', 'CardName', 'MainBoard')
    kwargs.setdefault('skip_blank_lines', True)
    kwargs.setdefault('comment', '#')
    kwargs.setdefault('names', colNames)
    return pd.read_csv(path, **kwargs)

def readMTGOStylecsv(path, **kwargs):
    """
    Read an MTGO style csv:
    """
    pass

def readMTGOStyledekFile(path, **kwargs):
    """
    Read an MTGO style dek file:
    """
    pass

def readExcel(path, **kwargs):
    """
    Read an xls file:
    """
    pass

def saveTCGStylecsv(path, **kwargs):
    """
    Write a TCG style csv:
    """
    pass
