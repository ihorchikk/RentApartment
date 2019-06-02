from django import forms


class FilterAndSearch(forms.Form):
    district = forms.CharField(label='district', required=False)
    rooms_count = forms.CharField(label='rooms_count', required=False)
    price_from = forms.IntegerField(label='price_from', required=False)
    price_to = forms.IntegerField(label='price_to', required=False)
