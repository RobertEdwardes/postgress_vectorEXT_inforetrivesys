from django import forms 

class SearchForm(forms.Form):
    query  = forms.CharField(label='Search Query')
    search_function = forms.ChoiceField(label='Group by Method', 
                                        choices=[
                                            ('L2Distance','L2Distance'),('MaxInnerProduct','MaxInnerProduct'),('CosineDistance','CosineDistance')
                                            ])
    max_return = forms.IntegerField(
        label='Limit Returns - Default 100',
        initial=100
    )