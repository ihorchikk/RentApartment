from django import forms


class Filter(forms.Form):
    district = forms.CharField(label='district', required=False)
    rooms_count = forms.CharField(label='rooms_count', required=False)
    price_from = forms.IntegerField(label='price_from', required=False)
    price_to = forms.IntegerField(label='price_to', required=False)
    search_data = forms.CharField(label='search_data', required=False)


class FilteredData(forms.Form):
    filter_data = forms.CharField(label='filter_data')