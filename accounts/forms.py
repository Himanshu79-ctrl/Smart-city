from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import  Worker


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'phone',
            'address',
            'password1',
            'password2',
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data["phone"]
        user.address = self.cleaned_data["address"]

        if commit:
            user.save()
        return user
    
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'email','phone', 'profile_pic']


COMMON_CLASS = "w-full p-2 rounded-lg bg-[#1e293b] text-white border border-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"


class StaffUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': COMMON_CLASS,
        'placeholder': 'Enter password'
    }))

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'phone', 'address', 'profile_pic']

        widgets = {
            'username': forms.TextInput(attrs={'class': COMMON_CLASS}),
            'email': forms.EmailInput(attrs={'class': COMMON_CLASS}),
            'phone': forms.TextInput(attrs={'class': COMMON_CLASS}),
            'address': forms.Textarea(attrs={'class': COMMON_CLASS, 'rows': 3}),
            'profile_pic': forms.FileInput(attrs={'class': "text-white"}),
        }


class WorkerForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ['department', 'date_of_joining']

        widgets = {
            'department': forms.Select(attrs={'class': COMMON_CLASS}),
            'date_of_joining': forms.DateInput(attrs={
                'class': COMMON_CLASS,
                'type': 'date'
            }),
        }
