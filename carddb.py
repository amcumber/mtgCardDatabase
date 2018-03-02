import pandas as pd
import numpy as np


# TODO
# Add a feature that will compare a df lib import (from self.import_lib) find
# SATICMETHODS
# refactor to use this method
# Move these to a tools lib??
# Expand on for new libs
# compile all sheets does not work
class CardDB(object):
    """
    Deck list or card library class
    
    Methods:
    :method add_card: Add card to lib
    :method remove_card: Remove card to lib
    :method replace_card: Replace card_out with card_in
    :method save: Save CardDB as card project (excel)
    :method new_lib: Make new lib
    :method import_lib: Import lib
    :method replace_lib: replace a lib with a new one
    :method del_lib: delete lib
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
                 populate_all_sheets=True,
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
        :param populate_all_sheets: bool - Used to populate optional sheets,
        such as
                change_log, sideboard, and maybeboard
        :param kwargs: dict() - keyword arguments to use in parser method
        """
        self.primary_sheet = None
        self.ExcelFileIO = None
        self.pandas_sheets = None

        # Private
        def _set_sheet_attr(sheet_name_, loc_):
            if loc_ is None:
                setattr(self, sheet_name_, None)
                # Check for required sheets
                if sheet_name_ is 'change_log':
                    print('Warning! Change Log not set!\nCreating one...')
                    self._format_change_log()
            elif (isinstance(loc_, int) or isinstance(loc_, float)
                  and parser is 'read_excel'):
                self.pandas_sheets[sheet_name_] = file_sheet_names.pop(loc_)
            elif parser is 'read_excel' and isinstance(loc_, str):
                file_sheet_names.pop(file_sheet_names.index(loc_))

        def _parse_sheet_name(sheet_name_, loc_):
            if loc_ is not None:
                if parser is 'read_excel':
                    kwargs['sheet_name'] = loc_
                sheet = parser_handle(self.filename, **kwargs)
                # Handle primary differently
                if sheet_name_ is 'primary_sheet':
                    if expand_composite:
                        sheet = self._expand_df(sheet, expand_on=expand_on)
                else:
                    sheet = self._sort_lib_on_key(sheet,
                                                  key=supporting_sheet_index,
                                                  drop=True)
                setattr(self, sheet_name_, sheet)

        def _populate_empty_sheets():
            empty_sheets = [sheet_name_ for sheet_name_, loc_ in
                            self.pandas_sheets.items() if loc_ is None]
            for sheet in empty_sheets:
                self.new_lib(sheet_name=sheet, force=True)

        # kwargs
        self.filename = filename
        parser_handle = getattr(pd, parser)
        if 'sheet_name' in kwargs.keys():
            primary_sheet = kwargs.pop('sheet_name')
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

    def save(self,
             filename=None,
             method='to_excel',
             sheet_name='primary_sheet',
             index=False):
        """
        Save Card_DB Object
        
        :param filename: str() - save location. If None, saves to self.filename
        :param method: str() - Method used to save pd.df obj, must be a 
                pd.df method
        :param sheet_name: pd.df object - Only used to save formats that are 
                not to_excel - Save specific object to filename.
        :param index: Used in save method to insert index to spreadsheet, 
        if True
        :return: None
        """
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
                    save_handle(writer, sheet_name=sheet_name, index=False)
                else:
                    print('Warning: "{}" not set!'.format(class_name))
            writer.save()
        else:
            sheet_handle = self._check_pandas_sheets(sheet_name)
            save_handle = getattr(sheet_handle, method)
            save_handle(filename, index=index)

    # TODO - expand_on
    def import_lib(self,
                   sheet_name,
                   data_frame,
                   force=False):
        """
        Import a pd.Dataframe lib into sheet_name

        :param sheet_name: sheet_name found in self.sheet_names
        :param data_frame: pd.DataFrame - lib data
        :param force: bool - add sheet_name to self.sheet_names
        :return: updated pd.df corresponding to sheet_name
        """
        if force:
            self._add_to_pandas_sheet(sheet_name)
        else:
            self._check_pandas_sheets(sheet_name)
        self.pandas_sheets[sheet_name] = sheet_name
        setattr(self, sheet_name, data_frame)
        return self._check_pandas_sheets(sheet_name)

    def new_lib(self,
                sheet_name,
                excel_name=None,
                columns=None,
                index=None,
                force=False):
        """
        Create new library. Available libraries are found in self.pandas_sheets
        
        :param sheet_name: str() - Sheet name found in pandas_sheet
        :param excel_name: str() - Name to be used in excel save
        :param columns: list() - Columns to be used in lib
        :param index: list() - Index to be used in lib
        :param force: bool - add sheet_name to self.sheet_names
        :return: pd.df - library constructed
        """
        if not force:
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
        setattr(self, sheet_name, pd.DataFrame(columns=columns, index=index))
        return self._check_pandas_sheets(sheet_name)

    # TODO - expand_on
    def replace_lib(self,
                    sheet_name,
                    data_frame,
                    keep_old_lib=False):
        """
        Replaces a lib with a new df

        :param sheet_name: str() - Sheet name found in pandas_sheet
        :param data_frame: pd.df - New data frame to use
        :param keep_old_lib: bool - Move old lib to '{}_old'.format(sheet_name)
        :return: new sheet_name df
        """
        if keep_old_lib:
            old_sheet_name = '{}_old'.format(sheet_name)
            self.import_lib(old_sheet_name,
                            data_frame=getattr(self, sheet_name),
                            force=True)
        setattr(self, sheet_name, data_frame)
        return self._check_pandas_sheets(sheet_name)

    def update_lib(self,
                   sheet_name,
                   data_frame,
                   key_field='Name',
                   secondary_key_field='Count',
                   keep_old_lib=False):
        """
        Similar to replace_lib but updates change log with differences between
        dfs

        :param sheet_name: str() - Sheet name found in pandas_sheet
        :param data_frame: pd.df - New data frame to use
        :param key_field: str() - col to use to match between the two dfs
        :param secondary_key_field: str() - col to use to match between the two
                dfs
        :param keep_old_lib: bool - Move old lib to '{}_old'.format(sheet_name)
        :return: new sheet_name df
        """
        def get_secondary_count(df, key_val):
            return sum(df[df[key_field] == key_val][secondary_key_field])

        def compare_a_to_b(a, b):
            mismatch_vals = []
            for val in set(a[key_field]):
                count_a = get_secondary_count(a, val)
                # A only
                if val not in data_frame[key_field]:
                    for _ in range(count_a):
                        mismatch_vals.append(val)
                # A & B for A > B
                else:
                    count_b = get_secondary_count(b, val)
                    for _ in range(count_a - count_b):
                        mismatch_vals.append(val)
            return mismatch_vals

        old_df = self._check_pandas_sheets(sheet_name)
        self.replace_lib(sheet_name, data_frame, keep_old_lib=keep_old_lib)

        out_cards = compare_a_to_b(old_df, data_frame)
        in_cards = compare_a_to_b(data_frame, old_df)

        for card in out_cards:
            self._update_change_log(card_out=card, location=sheet_name)

        for card in in_cards:
            self._update_change_log(card_in=card, location=sheet_name)
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

    def add_card(self,
                 card_obj=None,
                 log_change=True,
                 card_name_field='Name',
                 sheet_name='primary_sheet',
                 **card_vals):
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
        sheet_handle = self._check_pandas_sheets(sheet_name)
        if card_obj is None:
            card_obj = self._make_card_obj(sheet_name,
                                           force_new_fields=True,
                                           **card_vals)
        if log_change:
            new_name = card_obj.loc[0, card_name_field]
            self._update_change_log(card_in=new_name,
                                    location=self.pandas_sheets[sheet_name])
        # add card
        sheet_handle = self._connect_dfs(sheet_handle, card_obj)
        # save to original obj
        setattr(self, sheet_name, sheet_handle)
        return sheet_handle

    def remove_card(self, log_change=True, card_name_field='Name',
                    sheet_name='primary_sheet', **card_vals):
        """
        Remove a card from pd.df obj corresponding to sheet_name
        
        :param log_change: bool - Used to update self.card_log
        :param card_name_field: str() - Used to log card_name
        :param sheet_name: str() - str corresponding to pd.df obj to add card
        :param card_vals: dict() - Card values to Identify on, specifically 
        name
        :return: pd.df obj corresponding to sheet_name
        """
        sheet_handle = self._check_pandas_sheets(sheet_name)
        card_name = card_vals.pop(card_name_field)
        index = sheet_handle.query('{} == "{}"'.format(card_name_field,
                                                       card_name)).index.min()
        sheet_handle = sheet_handle.drop(index, axis=0)
        setattr(self, sheet_name, sheet_handle)
        if log_change:
            self._update_change_log(card_out=card_name,
                                    location=self.pandas_sheets[sheet_name])
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
                                    location=self.pandas_sheets[sheet_name])
        return self._check_pandas_sheets(sheet_name)

    # Consider making an __init__ nested method
    def _format_change_log(self):
        """
        Make a Change Log follow specific formatting
        :return: change_log
        """
        if self.pandas_sheets['change_log'] is None:
            self.change_log = pd.DataFrame({'Date': [],
                                            'In': [],
                                            'Out': [],
                                            'Location': []})
            self.pandas_sheets['change_log'] = 'change_log'
        else:
            template = ['Date', 'In', 'Out', 'Location']
            for col in template:
                missing = False
                if col not in self.change_log.columns:
                    missing = True
                if col.lower() in self.change_log.columns:
                    missing = False
                    vals = self.change_log[col.lower()]
                    new_log = self.change_log.assign(**{col: vals})
                    new_log.pop(col.lower())
                    self.change_log = new_log
                if missing:
                    self.change_log = self._add_sheet_field(self.change_log,
                                                            col)
            return self.change_log

    def _update_change_log(self,
                           card_in=None,
                           card_out=None,
                           location='primary_sheet',
                           date=None):
        """
        Update change_log if log exists
        
        :param card_in: Card name in
        :param card_out: Card name out
        :param location: sheet_name location
        :return: self.change_log
        """
        self._format_change_log()
        if date is None:
            date = pd.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if card_in is None:
            card_in = '--'
        if card_out is None:
            card_out = '--'
        log_entry = {'Date': date,
                     'In': card_in,
                     'Out': card_out,
                     'Location': location}
        self.change_log = self.add_card(**log_entry,
                                        log_change=False,
                                        sheet_name='change_log')
        return self.change_log

    def _check_pandas_sheets(self, sheet_name):
        """
        Check to see if sheet_name is in self.pandas_sheets
        
        :param sheet_name: str() - sheet name to be tested
        :return: sheet if present
        """
        if sheet_name not in self.pandas_sheets.keys():
            raise KeyError('Invalid sheet_name: {}, please use:\n'.format(
                ', '.join(self.pandas_sheets.keys())))
        return getattr(self, sheet_name)

    def _add_to_pandas_sheet(self, sheet_name):
        if sheet_name not in self.pandas_sheets.keys():
            self.pandas_sheets[sheet_name] = None

    def _make_card_obj(self,
                       sheet_name,
                       force_new_fields=False,
                       **card_data):
        sheet_handle = self._check_pandas_sheets(sheet_name)
        card_ = pd.DataFrame({field: [None] for field in sheet_handle.columns})
        for field, val in card_data.items():
            if field in sheet_handle.columns:
                card_.loc[0, field] = val
            elif force_new_fields:
                self._add_sheet_field(self.change_log, field)
            else:
                AttributeError('Field: "{}" not found in {}!'.format(
                        field, sheet_name))
        return card_

    # TODO -- refactor to use this method
    # TODO -- Move these to a tools lib??
    @staticmethod
    def _sort_lib_on_key(obj, key='Date', drop=False):
        """
        Format a lib with key as the index. Note: does not save to self!
        :param obj: pd.df - object to be formatted
        :return: pd.df object with index=key
        """
        obj.reset_index(inplace=True, drop=drop)
        obj.set_index(key)
        obj.sort_index()
        return obj

    # TODO -- Move these to a tools lib??
    def _expand_df(self, raw_df, expand_on, keep_expanded_col=True):
        """
        Expand a pd.df on a column
        
        :param raw_df: Object to work on
        :param expand_on: Column to expand
        :param keep_expanded_col: Does not delete expanded column, 
        but adjusts vals to 1's
        :return: Formatted pd.df
        """
        cols = [col for col in raw_df.columns if expand_on not in col]
        formatted_deck = pd.DataFrame(columns=raw_df.columns)
        iformat = 0
        for i in raw_df.index:
            for j in range(raw_df.loc[i, expand_on]):
                formatted_deck.loc[iformat] = raw_df.loc[i, cols]
                iformat += 1
        formatted_deck.pop(expand_on)
        if keep_expanded_col:
            formatted_deck = self._add_sheet_field(formatted_deck,
                                                   expand_on,
                                                   val=1)
        return formatted_deck

    # TODO -- Move these to a tools lib??
    @staticmethod
    def _add_sheet_field(old_df, field_name, val=np.nan):
        """
        Add a new column to a given sheet_name

        :param old_df: pd.df to work on 
        :param field_name: str() - new column / field name to be added to
                sheet_name
        :return: pd.df with added field
        """
        return old_df.assign(**{field_name: [val] * len(old_df)})

    @staticmethod
    def _connect_dfs(prime_df, secondary_df):
        prime_df = prime_df.append(secondary_df, ignore_index=True)
        prime_df.reset_index(drop=True, inplace=True)
        return prime_df

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


if __name__ == '__main__':
    print('Running Test for Card DB')
    # # Generate Spoof file
    import os

    cwd = os.getcwd()
    card_fh = '/'.join([cwd, 'card_list_tmp.csv'])
    # with open(card_fh) as f:
    #     pass
    # # Test import
    #
    # card = CardDB()
    # # Add card

    # # remove card

    # # swap card

    # # add lib

    # # import lib

    # # delete lib

    # # save

    # # Verify
