import requests
from bs4 import BeautifulSoup
from django import forms
from django.core.exceptions import ValidationError

from definitions import get_dictionary

# documentation how CELEX is identified: https://eur-lex.europa.eu/content/tools/eur-lex-celex-infographic-A3.pdf
def check(celex):
    if celex[0] != '3':
        raise ValidationError(
            'This type of sector is not supported, please enter a CELEX number of a regulation.'
        )
    if celex[1] != '1':
        if celex[1] != '2':
            raise ValidationError('The year of a regulation is invalid. ')
    if celex[5] != 'R':
        raise ValidationError('The legal document has to be a regulation. ')
    # check whether the regulation exists or not
    new_url = 'https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:' + \
        celex + '&from=EN'
    soup = BeautifulSoup(requests.get(new_url).text, 'html.parser')
    if soup.find('title').getText().__contains__(
            "The requested document does not exist"):
        raise ValidationError('The entered CELEX does not exist. ')
    # check whether a regulation contains a chapter definitions or not
    if soup.find("p", string="Definitions") is None:
        raise ValidationError(
            'The regulation does not contain legal definitions and cannot be processed. '
        )


def check_if_definition(definition):
    if definition not in get_dictionary().keys():
        raise ValidationError('The definition could not be found. ')


class FormCELEX(forms.Form):
    number = forms.CharField(
        label='Please enter a CELEX number of a regulation',
        min_length=10,
        max_length=10,
        validators=[check])


class FormDefinition(forms.Form):
    RELATIONS = (('hyponymy', 'Hyponymy'), ('synonymy', 'Synonymy'),
                 ('meronymy', 'Meronymy'))
    definition = forms.CharField(label='Please enter a legal definition',
                                 validators=[check_if_definition])
    relation = forms.ChoiceField(label='  Choose a relation',
                                 choices=RELATIONS,
                                 widget=forms.RadioSelect)
