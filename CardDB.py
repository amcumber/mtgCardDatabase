import pandas as pd
# import pickle
import datetime #add datetime to saveDb to default a unique val


# TODO
# Add a feature that will compare a df lib import (from self.import_lib) find
# differences between old and new
# 1. Add card_in and card_out in change_log
# 2. add feature to keep prev. sheet_handle under '{}_old'.format(sheet_name)
class CardDB(object):
    """
    Deck list or card library class
    
    Methods:
    :method add_card: Add card to lib
    :method remove_card: Remove card to lib
    :method replace_card: Replace card_out with card_in
    :method save: Save lib
    :method new_lib: Make new lib
    """
    def __init__(self, filename,
                 parser='read_excel',
                 primary_sheet=0,
                 change_log='Change_Log',
                 sideboard=None,
                 maybeboard=None,
                 expand_composite=False,
                 expand_on='Count',
                 supporting_sheet_index='Date',
                 # parse_all_sheets=False,  # TODO - do I really need this?
                 populate_all_sheets=False,
                 **kwargs):
        """
        Initialize CardDB from a saved lib
        
        :param filename: str() - filename to load lib into CardDb
        :param parser: pd method to read filename
        :param primary_sheet: str()/int() - location of decklist. Used only 
                for 'read_excel' parser
        :param change_log: str()/int() - name of change_log sheet. Used only 
                for 'read_excel' parser
        :param sideboard: str()/int() - name of sideboard sheet. Used only for 
                'read_excel' parser
        :param maybeboard: str()/int() - name of maybeboard sheet. Used only 
                for 'read_excel' parser
        :param expand_composite: bool - Used with 'expand_on' str. If 
                multiples are used, this bool will expand each multiple. 
                (e.g. 5 Islands expands to five independent entries of Island)
        :param expand_on: str() - Used with 'expand_composite' bool. Column 
                name to expand index
        :param supporting_sheet_index: str() - Index to be aligned for all 
                supporting indicies
#         :param parse_all_sheets: bool - Used to import all sheets from an
#                 excel file. Note: parser must be 'read_excel'
        :param populate_all_sheets: bool - Used to populate optional sheets,
        such as
                change_log, sideboard, and maybeboard
        :param kwargs: dict() - keyword arguments to use in parser method
        """
        self.primary_sheet = None
        self.ExcelFileIO = None
        self.pandas_sheets = None

        # Private
        def _parse_primary_sheet(raw_df):
            cols = [col for col in raw_df.columns if expand_on not in col]
            formatted_deck = pd.DataFrame(columns=raw_df.columns)
            iformat = 0
            for i in raw_df.index:
                for j in range(raw_df.loc[i, expand_on]):
                    formatted_deck.loc[iformat] = raw_df.loc[i, cols]
                    iformat += 1
            formatted_deck.pop(expand_on)
            return formatted_deck

        def _set_sheet_attr(sheet_name_, loc_):
            if loc_ is None:
                setattr(self, sheet_name_, None)
                # Check for required sheets
                if sheet_name_ is 'change_log':
                    print('Warning! Change Log not set!')
            elif (isinstance(loc_, int) or isinstance(loc_, float)
                  and parser is 'read_excel'):
                self.pandas_sheets[sheet_name_] = file_sheet_names.pop(loc_)
            elif parser is 'read_excel' and isinstance(loc_, str):
                file_sheet_names.pop(file_sheet_names.index(loc_))
            return None

        def _parse_sheet_name(sheet_name_, loc_):
            if loc_ is not None:
                if parser is 'read_excel':
                    kwargs['sheetname'] = loc_
                sheet = parser_handle(self.filename, **kwargs)
                # Handle primary differently
                if sheet_name_ is 'primary_sheet':
                    if expand_composite:
                        sheet = _parse_primary_sheet(sheet)
                else:
                    sheet = self._format_lib(sheet,
                                             key=supporting_sheet_index,
                                             drop=True)
                setattr(self, sheet_name_, sheet)
            return None

        def _populate_empty_sheets():
            empty_sheets = [sheet_name_ for sheet_name_, loc_ in
                            self.pandas_sheets.items() if loc_ is None]
            [self.new_lib(sheet_name=sheet) for sheet in empty_sheets]
            return None

        # kwargs
        self.filename = filename
        parser_handle = getattr(pd, parser)
        if 'sheetname' in kwargs.keys():
            primary_sheet = kwargs.pop('sheetname')
        if parser is 'read_excel':
            file_sheet_names = pd.ExcelFile(filename).sheet_names
            self.ExcelFileIO = pd.ExcelFile(filename)

        # Housekeeping - populate_sheets into housekeeping var
        self.pandas_sheets = {'primary_sheet': primary_sheet,
                              'change_log': change_log,
                              'sideboard': sideboard,
                              'maybeboard': maybeboard}
        for sheet_name, location in self.pandas_sheets.items():
            _set_sheet_attr(sheet_name, location)

        # Parse housekeeping sheets into vars
        for sheet_name, location in self.pandas_sheets.items():
            _parse_sheet_name(sheet_name, location)

        # check populate_all_sheets bool
        if populate_all_sheets:
            _populate_empty_sheets()

#         #TODO
#         # Add rest of sheets to index
#         if parse_all_sheets and parser is 'read_excel':
#             for val in file_sheet_names:
#                 self.pandas_sheets[val] = val

    def save(self, filename=None, method='to_excel',
             sheet_name='primary_sheet', **kwargs):
        """
        Save Card_DB Object
        
        :param filename: str() - save location. If None, saves to self.filename
        :param method: str() - Method used to save pd.df obj, must be a 
                pd.df method
        :param sheet_name: pd.df object - Only used to save formats that are 
                not to_excel - Save specific object to filename.
        :param kwargs: kwargs to input into 'format'
        :return: None
        """
        idx_bool = kwargs.pop('index', False)
        if filename is None:
            filename = self.filename
        if method is 'to_excel':
            writer = pd.ExcelWriter(filename)
            for class_name, sheet_name in self.pandas_sheets.items():
                if sheet_name is not None:
                    if isinstance(sheet_name, int):
                        sheet_name = class_name
                    sheet_handle = getattr(self, class_name)
                    save_handle = getattr(sheet_handle, method)
                    save_handle(writer, sheet_name=sheet_name, index=idx_bool,
                                **kwargs)
                else:
                    print('Warning: "{}" not set!'.format(class_name))
            writer.save()
        else:
            sheet_handle = getattr(self, sheet_name)
            save_handle = getattr(sheet_handle, method)
            save_handle(filename, index=idx_bool, **kwargs)

    def import_lib(self, sheet_name, data_frame=None, force=False):
        """
        Import a pd.Dataframe lib into sheet_name

        :param sheet_name: sheet_name found in self.sheet_names
        :param data_frame: pd.DataFrame - lib data
        :param force: bool - add sheet_name to self.sheet_names
        :return: getattr(self, sheet_name)
        """
        if force:
            self._add_to_pandas_sheet(sheet_name)
        self._check_pandas_sheets(sheet_name)
        self.pandas_sheets[sheet_name] = sheet_name
        setattr(self, sheet_name, data_frame)
        return getattr(self, sheet_name)

    def new_lib(self, sheet_name, excel_name=None,
                columns=None, index=None, **kwargs):
        """
        Create new library. Available libraries are found in self.pandas_sheets
        
        :param sheet_name: str() - Sheet name found in pandas_sheet
        :param excel_name: str() - Name to be used in excel save
        :param columns: list() - Columns to be used in lib
        :param index: list() - Index to be used in lib
        :param kwargs: dict() - keyword arguments to pass into pd.Dataframe 
                method
        :return: pd.df - library constructed
        """
        self._check_pandas_sheets(sheet_name)
        # update key
        if excel_name is None:
            excel_name = sheet_name
        self.pandas_sheets[sheet_name] = excel_name
        if columns is None:
            if sheet_name is 'change_log':
                columns = ['In', 'Out', 'Location']
            else:
                try:
                    columns = self.primary_sheet.columns
                except AttributeError:
                    columns = ['Name']
        if index is None:
            if sheet_name is 'change_log':
                index = ['Date']
            else:
                index = None
        # construct lib
        setattr(self, sheet_name, pd.DataFrame(columns=columns, index=index,
                                               **kwargs))
        return getattr(self, sheet_name)

    def delete_lib(self, sheet_name):
        """
        Delete a pd.df from pandas_sheets
        
        :param sheet_name: sheet name to be deleted
        :return: None
        """
        self._check_pandas_sheets(sheet_name)
        self.pandas_sheets[sheet_name] = None
        setattr(self, sheet_name, None)

    def add_card(self, card_obj=None, log_change=True, card_name_field='Name',
                 sheet_name='primary_sheet', **card_vals):
        """
        Add a card to pd.df obj corresponding to sheet_name
        
        :param card_obj: Card object (pd.df) to be added, not required
        :param log_change: bool - Used to update self.card_log
        :param card_name_field: str() - Used to log card_name
        :param sheet_name: str() - str corresponding to pd.df obj to add
                card to
        :param card_vals: dict() - Primary method to add a card. Required field
                includes card name field (eg Name=str())
        :return: pd.df obj corresponding to sheet_name
        """
        # init
        sheet_handle = getattr(self, sheet_name)
        if card_obj is None:
            card_obj = self._make_card_obj(sheet_name, **card_vals)
        if log_change:
            try:
                new_name = card_obj[card_name_field]
            except TypeError or KeyError:
                new_name = 'Unknown Name!'
            self._update_change_log(card_in=new_name, location=sheet_name)
        # add card
        sheet_handle = sheet_handle.append(card_obj, ignore_index=True)
        sheet_handle.reset_index(drop=True, inplace=True)
        # save to original obj
        setattr(self, sheet_name, sheet_handle)
        return sheet_handle

    def remove_card(self, log_change=True, card_name_field='Name',
                    sheet_name='primary_sheet', **card_vals):
        """
        Remove a card from pd.df obj corresponding to sheet_name
        
        :param card_obj: Card object (pd.df) to be added, not required
        :param log_change: bool - Used to update self.card_log
        :param card_name_field: str() - Used to log card_name
        :param sheet_name: str() - str corresponding to pd.df obj to add card to
        :param kwargs: dict() - Used to modify pd.df.drop method
        :return: pd.df obj corresponding to sheet_name
        """
        sheet_handle = getattr(self, sheet_name)
        card_name = card_vals.pop(card_name_field)
        index = sheet_handle.query('{} == "{}"'.format(card_name_field,
                                                       card_name)).index.min()
        sheet_handle = sheet_handle.drop(index, axis=0)
        setattr(self, sheet_name, sheet_handle)
        if log_change:
            self._update_change_log(card_out=card_name, location=sheet_name)
        return sheet_handle

    def replace_card(self, card_out=None, card_in=None,
                     log_change=True, card_name_field='Name',
                     sheet_name='primary_sheet'):
        """
        Replace a card from pd.df obj corresponding to sheet_name. Use a dict 
        for card_out and card_in to update decklist.
        
        :param card_out: dict() - requires 'card_name', optional inputs are
                found in remove_card method.
        :param card_in: dict() - requires add_card card name field (eg 
                Name=str()), optional inputs are found in add_card method
        :param log_change: bool - used to trigger _update_card_log method 
                and self.card_log df.
        :param card_name_field: str() - Used to log card_name
        :param sheet_name: str() - str corresponding to pd.df obj to add
                card to
        :return: pd.df obj corresponding to sheet_name
        """
        self.remove_card(log_change=False, sheet_name=sheet_name,
                         card_name_field=card_name_field, **card_out)
        self.add_card(log_change=False, sheet_name=sheet_name,
                      card_name_field=card_name_field, **card_in)
        if log_change:
            self._update_change_log(card_in=card_in[card_name_field],
                                    card_out=card_out[card_name_field],
                                    location=sheet_name)
        return getattr(self, sheet_name)

    # TODO - FIXME
    def _add_sheet_field(self, field_name, sheet_name='primary_sheet'):
        """
        Add a new column to a given sheet_name

        :param field_name: str() - new column / field name to be added to
                sheet_name
        :param sheet_name: str() - str corresponding to pd.df obj to add
                card to
        :return: pd.df obj corresponding to sheet_name
        """
        pass

    def _update_change_log(self, card_in=None, card_out=None,
                           location='primary_sheet', **kwargs):
        """
        Update change_log if log exists
        
        :param card_in: Card name in
        :param card_out: Card name out
        :param location: sheet_name location
        :param kwargs: used for custom date value. Use date=str()
        :return: self.change_log
        """
        # TODO - add 'location'
        def make_log_obj():
            log_dict = {}
            # TODO - wut??
            for field in self.change_log.columns:
                if 'date' in field.lower():
                    val = date
                elif 'out' in field.lower():
                    val = card_out
                elif 'in' in field.lower():
                    val = card_in
                elif 'location' in field.lower():
                    val = location
                else:
                    print('Unknown Field in change_log!')
                    break
                log_dict[field] = [val]
            return pd.DataFrame(log_dict)
        # FIXME FIXME
        # FIXME FIXME
        if True:
            raise AttributeError("Called _update_change_log FIXME")
        # FIXME FIXME
        # FIXME FIXME

        date = kwargs.pop('date', pd.datetime.now().strftime(
                '%Y-%m-%d %H:%M%S'))
        if card_in is None:
            card_in = '--'
        if card_out is None:
            card_out = '--'
        if self.change_log is not None:
            log_entry = make_log_obj()
            self.change_log.reset_index(inplace=True)
            self.change_log = self.change_log.append(log_entry,
                                                     ignore_index=True)
            self.change_log.set_index('date', inplace=True)
        else:
            print('change_log not set!')
        return self.change_log

    def _check_pandas_sheets(self, sheet_name):
        """
        Check to see if sheet_name is in self.pandas_sheets
        
        :param sheet_name: str() - sheet name to be tested
        :return: None
        """
        if sheet_name not in self.pandas_sheets.keys():
            raise KeyError('Invalid sheet_name: {}, please use:\n'.format(
                ', '.join(self.pandas_sheets.keys())))
        return None

    def _add_to_pandas_sheet(self, sheet_name):
        if sheet_name not in self.pandas_sheets.keys():
            self.pandas_sheets[sheet_name] = None

    def _make_card_obj(self, sheet_name, **card_data):
        sheet_handle = getattr(self, sheet_name)
        card_ = pd.DataFrame({field: [None] for field in sheet_handle.columns})
        for field, val in card_data.items():
            if field in sheet_handle.columns:
                card_.loc[0, field] = val
            else:
                print('Field: "{}" not found in {}!'.format(field, sheet_name))
        return card_

    # TODO -- refactor to use this method
    @staticmethod
    def _format_lib(obj, key='Date', **kwargs):
        """
        Format a lib with key as the index. Note: does not save to self!
        :param obj: pd.df - object to be formatted
        :param kwargs: dict() - additional args to pass into pd.df.reset_index
        :return: pd.df object with index=key
        """
        obj.reset_index(inplace=True, **kwargs)
        return obj.set_index(key)


# class Deck(CardDB):
#     def __init__(self, filename,
#                  parser='read_excel',
#                  expand_composite=False,
#                  **kwargs):
#         super.__init__()
#         self.game_cols = ['State']
# #         self.deck_list['State'] = [''] * len(self.deck_list)
#
#     def draw_hand(self, n=7):
#         for i in range(n):
#             self.draw_card()
#         return self.get_state('hand')
#
#     def draw_card(self, state='hand'):
#         lib = self.get_state('library').reset_index()
#         i = np.random.randint(0,len(lib))
#         orig_idx = lib.loc[i, 'index']
#         self.deck_list.loc[orig_idx, 'State'] = state
#         return self.deck_list.loc[orig_idx]
#
#     def get_state(self, state):
#         return self.deck_list[self.deck_list['State'] == state]
#
#     def start_game(self):
#         self.reset_deck()
#         self.draw_hand()
#         # TODO
#
#     def reset_deck(self):
#         pass
#         # self.deck_list['State'] = ['library'] * len(self.deck_list)
#         # self._info.combineAdd(card.getCardInfo)
#
