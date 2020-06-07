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
        labels = {'name': 'Nazwa', 'discipline': 'Dyscyplina', 'start_date': 'Data rozpoczęcia (DD.MM.YYYY HH:MM:SS)',
                  'registration_deadline': 'Koniec rejestracji (DD.MM.YYYY HH:MM:SS)',
                  'participants_limit': 'Limit uczestników', 'city': 'Miasto', 'street': 'Ulica', 'number': 'Nr domu'}

    '''def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['registration_deadline'] > cleaned_data['start_date']:
            raise forms.ValidationError('Zapisy na turniej muszą zakończyć się przed jego rozpoczęciem')
        if cleaned_data['registration_deadline'] <= timezone.now():
            raise forms.ValidationError('Nie mozna dodać turnieju z przeszłości')
        if cleaned_data['participants_limit'] <= 0:
            raise forms.ValidationError('Limit zawodników musi być większy od 0')
        return cleaned_data'''
    def clean_registration_deadline(self):
        try:
            start = self.cleaned_data['start_date']
        except KeyError:
            raise forms.ValidationError()
        try:
            registration = self.cleaned_data['registration_deadline']
        except KeyError:
            raise forms.ValidationError()
        if registration >= start:
            raise forms.ValidationError('Zapisy na turniej muszą zakończyć się przed jego rozpoczęciem')
        if registration <= timezone.now():
            raise forms.ValidationError('Nie mozna dodać turnieju z przeszłości')
        return registration

    def clean_participants_limit(self):
        limit = int(self.cleaned_data['participants_limit'])
        if limit <= 0:
            raise forms.ValidationError('Limit zawodników musi być większy od 0')
        return limit


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

    def clean_registration_deadline(self):
        try:
            start = self.cleaned_data['start_date']
        except KeyError:
            raise forms.ValidationError()
        try:
            registration = self.cleaned_data['registration_deadline']
        except KeyError:
            raise forms.ValidationError()
        if registration >= start:
            raise forms.ValidationError('Zapisy na turniej muszą zakończyć się przed jego rozpoczęciem')
        if registration <= timezone.now():
            raise forms.ValidationError('Nie mozna ustawić daty turnieju z przeszłości')
        return registration

    def clean_participants_limit(self):
        limit = self.cleaned_data['participants_limit']
        if limit <= 0:
            raise forms.ValidationError('Limit zawodników musi być większy od 0')
        if limit < self.participants:
            raise forms.ValidationError(
                'Limit zawodników nie może być mniejszy niż zgłoszona dotychczas liczba (' + str(self.participants) + ')')
        return limit


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
