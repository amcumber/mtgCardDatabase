"""
Workflow:
xml >> 
hash (sets >> hash// cards >> hash) >> 
hash ( sets >> obj // cards >> obj) >> 
hash (sets >> cards)
"""
__all__ = ['unpack_cards_xml']


# Public
class CockatriceEntry(object):
    def __init__(self, unpacked_obj):
        for key, val in unpacked_obj.items():
            setattr(self, key, val)


class SetEntry(object):
    def __init__(self, set_obj):
        for key, val in set_obj.__dict__.items():
            setattr(self, key, val)
        self.cards = []

    def __str__(self):
        return self.name


# Private
def _unpack_cockatrice_object(xml_object):
    """
    Return a dict of a cockatrice xml object --
    -- not to be confused with a CockatriceEntry
    """
    unpacked_obj = dict()
    for tag_obj in xml_object:
        if tag_obj.tag == 'set':
            try:
                unpacked_obj['sets']
            except KeyError:
                unpacked_obj['sets'] = []
                unpacked_obj['muIds'] = {}
            unpacked_obj['sets'].append(tag_obj.text)
            unpacked_obj['muIds'][tag_obj.text] = tag_obj.attrib['muId']
        else:
            unpacked_obj[tag_obj.tag] = tag_obj.text
    return unpacked_obj


def _unpack_primary_branch(xml_branch):
    """Return a generator of a primary branch from a cockatrice xml"""
    return (_unpack_cockatrice_object(packed_obj) for packed_obj in xml_branch)


def unpack_cockatrice_xml(filename, silent=False):
    """
    Unpack a generic cockatrice xml into primary_banches>>
    child_cockatrice_objects
    """
    import xml.etree.ElementTree as ET
    root = ET.parse(filename).getroot()
    if not silent:
        print('Unpacking: {0}'.format(root.tag))
        for k, v in root.attrib.items():
            print('{0}: {1}'.format(k, v))
    primary_branches = {child.tag: list(_unpack_primary_branch(child))
                        for child in root}
    repacked_branches = {name: [CockatriceEntry(unpacked_obj)
                                for unpacked_obj in branch]
                         for name, branch in primary_branches.items()}
    return repacked_branches


def _remap_unorganized_carddatabase(repacked_carddatabase):
    """
    Remap generic repacked_branches hash to an organized hash of set>>cards"""
    organized_db = {}
    for set_obj in repacked_carddatabase['sets']:
        organized_db[set_obj.name] = SetEntry(set_obj)
    for card_obj in repacked_carddatabase['cards']:
        [organized_db[set_].cards.append(card_obj) for set_ in card_obj.sets]
    return organized_db


# Public
def unpack_cards_xml(filename, silent=False):
    """Unpack cards.xml from Cockatrice's Oracle"""
    generic_unpack = unpack_cockatrice_xml(filename, silent=silent)
    return _remap_unorganized_carddatabase(generic_unpack)
