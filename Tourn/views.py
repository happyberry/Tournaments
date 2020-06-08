from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import *
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from .models import Tournament, Game, Logo, Participation
from django.contrib import messages
from random import shuffle
import datetime
import math
import random


# Create your views here.
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.is_active = False
            user.save()
            print(user.username)
            current_site = get_current_site(request)
            mail_subject = 'Aktywuj swoje konto w Tournaments'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            print(message)
            email.send(fail_silently=True)
            return HttpResponse('Please confirm your email address to complete the registration')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')


def post_list(request):
    if 'search' in request.POST:
        name = request.POST["tournament_name"]
    else:
        name = ""
    queryset_list = Tournament.objects.filter(start_date__gte=datetime.date.today()).order_by("start_date")
    if len(name) != 0:
        print("name", name)
        queryset_list = queryset_list.filter(name__contains=name)
    paginator = Paginator(queryset_list, 10)  # posts per page
    page = request.GET.get('page')
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)
    context = {
        "object_list": queryset,
        'name': name,
        'length': len(queryset_list)
    }
    return render(request, "home.html", context)


def my_list(request):
    participations = Participation.objects.filter(user=request.user)
    queryset_list = []
    for p in participations:
        queryset_list.append(p.tournament)
    #queryset_list = Tournament.objects.filter(start_date__gte=datetime.date.today()).order_by("start_date")
    #queryset_list = queryset_list.filter()
    paginator = Paginator(queryset_list, 10)  # posts per page
    page = request.GET.get('page')
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)
    context = {
        "object_list": queryset,
        'length': len(queryset_list)
    }
    return render(request, "my.html", context)


def my_games(request):
    queryset_list = Game.objects.filter(Q(user1=request.user) | Q(user2=request.user))
    paginator = Paginator(queryset_list, 10)  # posts per page
    page = request.GET.get('page')
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)
    context = {
        "object_list": queryset,
        'length': len(queryset_list)
    }
    return render(request, "my_games.html", context)


def nextPlayer(x):
    out = []
    length = len(x) * 2 + 1
    for i in x:
        out.append(i)
        out.append(length - i)
    return out


def seed(number):
    rounds = round(math.log(number) / math.log(2) - 1)
    pls = [1, 2]
    for i in range(rounds):
        pls = nextPlayer(pls)
    return pls


def generate_bracket1(tourn, participants_number):
    n = round(math.log(participants_number, 2))
    k = participants_number - 2 ** n
    if k == 0:
        games_counter = 2**(n-1)
        limit = 2**n
    else:
        games_counter = 2**n
        limit = 2**(n+1)
    bracket_sequence = seed(limit)
    for s in range(len(bracket_sequence)):
        bracket_sequence[s] -= 1
    print(bracket_sequence)
    participants = list(Participation.objects.filter(tournament=tourn).order_by('rank'))
    games = []
    for i in range(1, limit):
        days = n + 2 - round(math.log(i, 2))
        newgame = Game(matchno=i,date=tourn.start_date + datetime.timedelta(days=days), tournament=tourn)
        games.append(newgame)
    for i in range(0, len(bracket_sequence), 2):
        print(bracket_sequence[i], bracket_sequence[i+1])
        if bracket_sequence[i] < participants_number and bracket_sequence[i+1] < participants_number:
            games[games_counter-1].user1 = participants[bracket_sequence[i]].user
            games[games_counter-1].user2 = participants[bracket_sequence[i+1]].user
            print(games_counter, participants[bracket_sequence[i]].user.first_name, participants[bracket_sequence[i+1]].user.first_name)
            games_counter += 1
        elif bracket_sequence[i] < participants_number and bracket_sequence[i+1] >= participants_number:
            if games_counter % 2 == 0:
                games[(games_counter // 2) - 1].user1 = participants[bracket_sequence[i]].user
                #games[(games_counter // 2) - 1].score = 3
            else:
                games[(games_counter // 2) - 1].user2 = participants[bracket_sequence[i]].user
                #games[(games_counter // 2) - 1].score = 3
            print(games_counter//2, participants[bracket_sequence[i]].user.first_name)
            games_counter += 1
        elif bracket_sequence[i] >= participants_number and bracket_sequence[i+1] < participants_number:
            if games_counter % 2 == 0:
                games[(games_counter // 2) - 1].user1 = participants[bracket_sequence[i+1]].user
                #games[(games_counter // 2) - 1].score = 3
            else:
                games[(games_counter // 2) - 1].user2 = participants[bracket_sequence[i + 1]].user
                #games[(games_counter // 2) - 1].score = 3
            print(games_counter // 2, participants[bracket_sequence[i+1]].user.first_name)
            games_counter += 1
    for i in range(len(games)):
        games[i].save()


def generate_bracket(tourn, participants_number):
    n = round(math.log(participants_number, 2))
    k = participants_number - 2**n
    participants1 = list(Participation.objects.filter(tournament=tourn).order_by('rank')[:2*k])
    participants2 = list(Participation.objects.filter(tournament=tourn).order_by('rank')[2*k:])
    print("n:", n)
    print("k:", k)
    print("len(participants1):", participants1.count())
    games = []
    if k != 0:
        limit = 2**(n+1)
    else:
        limit = 2**n
    all = limit-1
    for i in range(1, limit):
        days = n + 2 - round(math.log(i, 2))
        newgame = Game(matchno=i+1,date=tourn.start_date + datetime.timedelta(days=days))
        games.append(newgame)
    closed1 = []
    closed2 = []
    for i in range(0, len(participants1), 2):
        games[all - i // 2 - 1].user1 = participants1[i]
        games[all - i // 2 - 1].score = 0
        games[all - i // 2 - 1].user2 = participants1[i+1]
        games[all - i // 2 - 1].score = 0
        if (i//2) % 2 == 0:
            closed2.append((all - i // 2 - 1)//2)
        else:
            closed1.append((all - i // 2 - 1)//2)
    participantcounter = 0
    for i in range(2**(n-2), 2**(n-1), 1):
        if participantcounter < len(participants2):
            if i not in closed1:
                games[i-1].user1 = participants2[participantcounter]
                games[i-1].score = 0
                participantcounter += 1
        if participantcounter < len(participants2):
            if i not in closed2:
                games[i-1].user2 = participants2[participantcounter]
                games[i-1].score = 0
                participantcounter += 1
    for i in range(len(games)):
        games[i].save()


def tournament_info(request, id):
    user = request.user
    try:
        tourn = Tournament.objects.get(id=id)
    except Tournament.DoesNotExist:
        raise Http404("Nie ma takiego turnieju")
    try:
        logos = Logo.objects.filter(tournament=tourn)
    except Logo.DoesNotExist:
        logos = []
    try:
        organizer = User.objects.get(id=tourn.organizer_id)
        name = organizer.first_name + " " + organizer.last_name
    except User.DoesNotExist:
        name = "Nieznany"
    try:
        participants = Participation.objects.filter(tournament=tourn).count()
    except Participation.DoesNotExist:
        participants = 0
    show = False
    if tourn.registration_deadline > timezone.now():
        show = True
    #if show == False and Game.objects.filter(tournament=tourn).count() == 0:
    generate_bracket1(tourn, participants)
    context = {
        'tourn': tourn,
        'logos': logos,
        'organizer': name,
        'participants': participants,
        'user': user,
        'show': show
    }
    return render(request, 'tournaments/detail.html', context)


def add_tournament(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = AddTournamentForm(request.POST)
            if form.is_valid():
                tournament = form.save(commit=False)
                tournament.organizer = request.user
                tournament.save()
                current_site = get_current_site(request)
                return redirect('/../tournament/' + str(tournament.id))
        else:
            form = AddTournamentForm()
        return render(request, 'tournaments/add.html', {'form': form})
    else:
        return redirect('login')


def edit_tournament(request, id):
    try:
        tourn = Tournament.objects.get(id=id)
    except Tournament.DoesNotExist:
        raise Http404("Nie ma takiego turnieju")
    try:
        participants = Participation.objects.filter(tournament=tourn)
        participants_number = len(participants)
    except Participation.DoesNotExist:
        pass
    if request.user.is_authenticated:
        if request.method == 'POST':
            if request.user.id == tourn.organizer_id and tourn.registration_deadline > timezone.now():
                form = EditTournamentForm(request.POST, instance=tourn, participants=participants_number, start=tourn.start_date)

                if form.is_valid():
                    tournament = form.save(commit=False)
                    tournament.save()
                    return redirect('/../tournament/' + str(tournament.id))
            else:
                if tourn.registration_deadline <= timezone.now():
                    messages.add_message(request, messages.INFO, 'Nie możesz edytować informacji o turnieju, który już się rozpoczął')
                else:
                    messages.add_message(request, messages.INFO,'Nie możesz edytować informacji o turnieju, którego organizatorem nie jesteś')
                form = EditTournamentForm(instance=tourn, participants=participants_number, start=tourn.start_date)
                return render(request, 'tournaments/edit.html', {'form': form, 'participants_number': participants_number, 'tourn': tourn})
        else:
            form = EditTournamentForm(instance=tourn, participants=participants_number, start=tourn.start_date)
        return render(request, 'tournaments/edit.html', {'form': form, 'participants_number': participants_number, 'tourn': tourn})
    else:
        return redirect('login')


def add_logo(request, id):
    try:
        tourn = Tournament.objects.get(id=id)
    except Tournament.DoesNotExist:
        raise Http404("Nie ma takiego turnieju")
    try:
        logos = Logo.objects.filter(tournament=tourn)
    except Logo.DoesNotExist:
        logos = {}
    if request.user.is_authenticated:
        if request.user.id == tourn.organizer_id:
            if request.method == 'POST':
                form = AddLogoForm(request.POST, request.FILES)
                if form.is_valid():
                    image = request.FILES['obraz']
                    filename = str(tourn.id) + str(tourn.name)
                    filename += request.FILES['obraz'].name
                    handle_uploaded_file(image, filename)
                    logo = Logo(image_src='Tourn/static/' + filename, tournament=tourn)
                    logo.save()
                    try:
                        logos = Logo.objects.filter(tournament=tourn)
                    except Logo.DoesNotExist:
                        logos = {}
                    form = AddLogoForm()
                    return render(request, 'tournaments/add_logo.html', {'logos': logos, 'form':form})
            else:
                form = AddLogoForm()
        else:
            return redirect('/../tournament/' + str(tourn.id))
        return render(request, 'tournaments/add_logo.html', {'logos': logos, 'form':form})
    else:
        return redirect('login')


def handle_uploaded_file(f, name):
    with open('Tourn/static/' + name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def join_tournament(request, id):
    try:
        tourn = Tournament.objects.get(id=id)
    except Tournament.DoesNotExist:
        raise Http404("Nie ma takiego turnieju")
    try:
        participants = Participation.objects.filter(tournament=tourn)
        participants_number = len(participants)
    except Participation.DoesNotExist:
        pass
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = AddParticipationForm(request.POST, tournament=tourn)
            if participants_number >= tourn.participants_limit or tourn.registration_deadline <=  timezone.now():
                if participants_number >= tourn.participants_limit:
                    messages.add_message(request, messages.INFO, 'Przepraszamy, limit uczestników został już osiągnięty')
                else:
                    messages.add_message(request, messages.INFO, 'Przepraszamy, termin zgłoszeń upłynął')
                try:
                    logos = Logo.objects.filter(tournament=tourn)
                except Logo.DoesNotExist:
                    logos = []
                try:
                    organizer = User.objects.get(id=tourn.organizer_id)
                    name = organizer.first_name + " " + organizer.last_name
                except User.DoesNotExist:
                    name = "Nieznany"
                try:
                    participants = Participation.objects.filter(tournament=tourn).count()
                except Participation.DoesNotExist:
                    participants = 0
                show = False
                if tourn.registration_deadline > timezone.now():
                    show = True
                return render(request, 'tournaments/detail.html', {'tourn': tourn,
                'logos': logos,
                'organizer': name,
                'participants': participants,
                'user': request.user,
                'show': show})
                #return redirect('/../')
            if form.is_valid():
                participation = form.save(commit=False)
                participation.user = request.user
                participation.tournament = tourn
                participation.save()
                return redirect('/../')
        else:
            form = AddParticipationForm(tournament=tourn)
        return render(request, 'tournaments/join.html', {'form': form})
    else:
        return redirect('login')
