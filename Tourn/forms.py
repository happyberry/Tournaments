from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.utils import timezone

from .models import *


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')
        labels = {'first_name': "Imię", 'last_name': "Nazwisko", 'password1': "Hasło", 'password2': "Potwierdź hasło"}


class SearchForm(forms.Form):
    nazwa = forms.CharField(help_text="Podaj nazwę (lub jej fragment)", required=True)


class AddTournamentForm(ModelForm):
    class Meta:
        model = Tournament
        fields = ['name', 'discipline', 'start_date', 'registration_deadline', 'participants_limit', 'city', 'street',
                  'number']
        labels = {'name': 'Nazwa', 'discipline': 'Dyscyplina', 'start_date': 'Data rozpoczęcia',
                  'registration_deadline': 'Koniec rejestracji',
                  'participants_limit': 'Limit uczestników', 'city': 'Miasto', 'street': 'Ulica', 'number': 'Nr domu'}

    @property
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['registration_deadline'] > cleaned_data['start_date']:
            print("problem1")
            raise forms.ValidationError('Zapisy na turniej muszą zakończyć się przed jego rozpoczęciem')
        if cleaned_data['registration_deadline'] <= timezone.now():
            raise forms.ValidationError('Nie mozna dodać turnieju z przeszłości')
            print("problem2")
        if cleaned_data['participants_limit'] <= 0:
            print("problem3")
            raise forms.ValidationError('Limit zawodników musi być większy od 0')
        return cleaned_data


class EditTournamentForm(ModelForm):
    participants = 0
    start = timezone.now()

    def __init__(self, *args, **kwargs):
        self.participants = kwargs.pop('participants')  # cache the user object you pass in
        self.start = kwargs.pop('start')
        super(ModelForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Tournament
        fields = ['start_date', 'registration_deadline', 'participants_limit', 'city', 'street', 'number']
        labels = {'name': 'Nazwa', 'discipline': 'Dyscyplina', 'start_date': 'Data rozpoczęcia',
                  'registration_deadline': 'Koniec rejestracji',
                  'participants_limit': 'Limit uczestników', 'city': 'Miasto', 'street': 'Ulica', 'number': 'Nr domu'}

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['participants_limit'] <= 0:
            raise forms.ValidationError('Limit zawodników musi być większy od 0')
        if cleaned_data['participants_limit'] < self.participants:
            raise forms.ValidationError(
                'Limit zawodników nie może być mniejszy niż zgłoszona dotychczas liczba (' + str(self.participants) + ')')
        return cleaned_data


class AddLogoForm(forms.Form):
    obraz = forms.ImageField()


class AddParticipationForm(ModelForm):
    tournament = Tournament()

    def __init__(self, *args, **kwargs):
        self.tournament = kwargs.pop('tournament')  # cache the user object you pass in
        super(ModelForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Participation
        exclude = ['user', 'tournament']
        labels = {'license': "Nr licencji", 'rank': "Aktualny ranking"}

    def clean(self):
        cleaned_data = super().clean()
        try:
            participants = Participation.objects.filter(tournament=self.tournament)
            participants_number = len(participants)
        except Participation.DoesNotExist:
            pass
        return cleaned_data
