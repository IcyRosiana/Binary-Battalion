from django.contrib.auth.models import User
from .models import Stock, Category, Stock_History_log
from django import forms
from django.core.validators import MinLengthValidator

#ok na 
class StockUpdateForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['category', 'item_name']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        stock = super().save(commit=False)
        stock.updated_by = self.request.user.username
        if commit:
            stock.save()
        return stock




class BaseModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        username = kwargs.pop('username', None)
        super().__init__(*args, **kwargs)
        self.fields['issue_by'].initial = username
        self.fields['issue_by'].disabled = True


class IssueForm(forms.ModelForm):
    issue_by = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), label='Issued By', required=True)
    issue_to = forms.CharField(label='Issued To', required=True)

    class Meta:
        model = Stock
        fields = ['issue_quantity', 'issue_by', 'issue_to']

    def clean_issue_to(self):
        issue_to = self.cleaned_data.get('issue_to')
        if not issue_to:
            raise forms.ValidationError('This field is required')
        return issue_to



#ok na 
class ReceiveForm(forms.ModelForm):
    receive_by = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Stock
        fields = ['receive_quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['receive_quantity'].widget.attrs['min'] = 1

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.receive_by = self.cleaned_data['receive_by']
        if commit:
            instance.save()
        return instance




 #ok na    
class ReorderLevelForm(forms.ModelForm):
    current_user = forms.CharField(label='Updated by', widget=forms.TextInput(attrs={'readonly': 'readonly'}), required=False)

    class Meta:
        model = Stock
        fields = ['reorder_level', 'current_user']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['current_user'].initial = self.request.user.username

    def save(self, commit=True):
        stock = super().save(commit=False)
        if commit:
            stock.save()
        return stock


class StockHistorySearchForm(forms.ModelForm):
    export_to_CSV = forms.BooleanField(required=False)  
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    class Meta:
        model = Stock_History_log
        fields = ['category', 'item_name']

#ok na 
class StockSearchForm(forms.ModelForm):
    export_to_CSV = forms.BooleanField(required=False)
    sort_order = forms.ChoiceField(choices=[('ascending', 'Ascending'), ('descending', 'Descending'),('-----', '-----')], required=False, label='Sort Order')
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    class Meta:
        model = Stock
        fields = ['category', 'item_name']


#ok na 
class StockCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['created_by'] = forms.CharField(initial=user.username, label='Created By', required=True, widget=forms.TextInput(attrs={'readonly': True}))
               
    class Meta:
        model = Stock
        fields = ['category', 'item_name', 'quantity', 'reorder_level']
        widgets = {
            'category': forms.Select(attrs={'required': True}),
            'item_name': forms.TextInput(attrs={'required': True}),
        }
        validators = {
            'item_name': [MinLengthValidator(1)],
        }

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise forms.ValidationError('This field is required')
        return category

    def clean_item_name(self):
        item_name = self.cleaned_data.get('item_name').upper()
        if not item_name:
            raise forms.ValidationError('This field is required')
        for instance in Stock.objects.all():
            if instance.item_name.upper() == item_name:
                raise forms.ValidationError(str(item_name) + ' is already created')
        return item_name.upper()


#OK na
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError('This field is required')
        name = name.upper()
        for instance in Category.objects.all():
            if instance.name.upper() == name:
                raise forms.ValidationError(str(name) + ' already exists')
        return name
