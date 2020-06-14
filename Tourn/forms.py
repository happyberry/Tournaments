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
        labels = {'name': 'Nazwa', 'discipline': 'Dyscyplina', 'start_date': 'Data rozpoczęcia (DD.MM.RRRR GG:MM:SS)',
                  'registration_deadline': 'Koniec rejestracji (DD.MM.RRRR GG:MM:SS)',
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
        if limit <= 1:
            raise forms.ValidationError('Minimalna liczba zawodników to 2')
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
        if limit <= 1:
            raise forms.ValidationError('Minimalna liczba zawodników to 2')
        if limit < self.participants:
            raise forms.ValidationError(
                'Limit zawodników nie może być mniejszy niż zgłoszona dotychczas liczba (' + str(self.participants) + ')')
        return limit


class AddLogoForm(forms.Form):
    obraz = forms.ImageField()


class AddParticipationForm(ModelForm):
    tournament = Tournament()
    user = User()

    def __init__(self, *args, **kwargs):
        self.tournament = kwargs.pop('tournament')  # cache the user object you pass in
        self.user = kwargs.pop('user')
        super(ModelForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Participation
        exclude = ['user', 'tournament']
        labels = {'license': "Nr licencji", 'rank': "Aktualny ranking"}

    '''def clean(self):
        cleaned_data = super().clean()
        try:
            participant = Participation.objects.filter(tournament=self.tournament).filter(user=self.user)
            if participant.count() != 0:
                raise forms.ValidationError('Nie możesz zapisać się ponownie na ten sam turniej')
        except Participation.DoesNotExist:
            pass
        return cleaned_data'''

class SubmitScoreForm(forms.Form):
    winner = forms.ModelChoiceField(label='Select the winner', queryset=User.objects.all())

    def __init__(self, *args, **kwargs):
        matchid = kwargs.pop('matchid', None)  # cache the user object you pass
        id_list = [Game.objects.get(id=matchid).user1_id, Game.objects.get(id=matchid).user2_id]
        queryset = User.objects.filter(id__in=id_list)
        super(SubmitScoreForm, self).__init__(*args, **kwargs)
        self.fields['winner'].queryset = queryset
        self.fields['winner'].label_from_instance = lambda obj: "%s" % obj.get_full_name()
