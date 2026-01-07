
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg
from .models import Service, Booking, Master, Location, Review

def home(request):
    sort = request.GET.get('sort', '')
    if sort == 'asc': services = Service.objects.all().order_by('price')
    elif sort == 'desc': services = Service.objects.all().order_by('-price')
    else: services = Service.objects.all()

    masters = Master.objects.all()
    locations = Location.objects.all()
    loc_html = "".join([f'<p><i class="material-icons left">location_on</i> {l.city}, {l.address}</p>' for l in locations])

    if request.user.is_authenticated:
        auth = f'''<li><a href="/profile/" class="btn green darken-1 waves-effect waves-light" style="margin-right:10px;">📅 МОЇ ЗАПИСИ</a></li><li><a href="/logout/" class="red-text">ВИХІД ({request.user.username})</a></li>'''
        cta = '<a href="/book/" class="btn-large orange darken-3 pulse">ЗАПИСАТИСЯ</a>'
    else:
        auth = '<li><a href="/login/">Вхід</a></li><li><a href="/register/" class="orange-text">Реєстрація</a></li>'
        cta = '<a href="/register/" class="btn-large green darken-2">Стати клієнтом</a>'

    s_html = "".join([f'<div class="col s12 m4"><a href="/book/" style="color:inherit;"><div class="card hoverable z-depth-2"><div class="card-content center"><span class="card-title"><b>{s.name}</b></span><p class="grey-text">{s.description}</p><h5 class="green-text">{s.price} грн</h5><small class="orange-text">Натисніть для запису</small></div></div></a></div>' for s in services])
    m_html = "".join([f'<div class="col s12 m4"><a href="/master/{m.id}/" style="color:inherit;"><div class="card hoverable"><div class="card-image"><img src="{m.photo_url}" style="height:250px;object-fit:cover"></div><div class="card-content center"><span class="card-title"><b>{m.name}</b></span><p class="orange-text">{"★"*int(m.rating)} ({m.rating})</p><p class="grey-text">{m.reviews_count} відгуків</p><button class="btn-small grey darken-3" style="width:100%">Профіль</button></div></div></a></div>' for m in masters])
    map_html = '<iframe width="100%" height="300" frameborder="0" scrolling="no" src="https://www.openstreetmap.org/export/embed.html?bbox=30.518,50.448,30.525,50.453&amp;layer=mapnik&amp;marker=50.450,30.522"></iframe>'

    return HttpResponse(f'''<!DOCTYPE html><html lang="uk"><head><title>BarberShop</title><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css"><link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet"><style>body{{background:#f5f5f5;font-family:'Roboto',sans-serif}} .hero{{background:linear-gradient(rgba(0,0,0,0.7),rgba(0,0,0,0.7)),url('https://images.unsplash.com/photo-1585747860715-2ba37e788b70?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80');background-size:cover;height:550px;display:flex;align-items:center;justify-content:center;color:white;text-align:center}} nav{{background:transparent;box-shadow:none;position:absolute;width:100%;z-index:999}} .section-header{{text-align:center;margin:60px 0 40px;text-transform:uppercase;letter-spacing:2px;font-weight:bold;color:#333}}</style></head><body>
        <nav><div class="nav-wrapper container"><a href="/" class="brand-logo"><i class="material-icons left">content_cut</i>BARBER</a><ul class="right hide-on-med-and-down"><li><a href="#services">Послуги</a></li><li><a href="#masters">Майстри</a></li><li><a href="#about">Про нас</a></li>{auth}</ul></div></nav>
        <div class="hero"><div class="container"><h1 style="font-weight:900;text-transform:uppercase">Твій Стиль.</h1><br>{cta}</div></div>
        <div id="services" class="container"><h4 class="section-header">Прайс-лист</h4><div class="center" style="margin-bottom:20px"><a href="?sort=asc" class="btn waves-effect grey darken-3">Дешевше</a> <a href="?sort=desc" class="btn waves-effect grey darken-3">Дорожче</a></div><div class="row">{s_html}</div></div>
        <div id="masters" class="grey lighten-3" style="padding:40px 0"><div class="container"><h4 class="section-header">Команда</h4><div class="row">{m_html}</div></div></div>
        <div id="about" class="container" style="padding:60px 0;text-align:center"><h4 class="section-header">Про нас</h4><p class="flow-text">Атмосфера, віскі, стиль.</p></div>
        <div class="grey darken-4 white-text" style="padding:60px 0"><div class="container"><div class="row"><div class="col s12 m6"><h5>Контакти</h5>{loc_html}<p><i class="material-icons left">phone</i> +380 99 123 45 67</p></div><div class="col s12 m6">{map_html}</div></div></div></div>
        <footer class="black page-footer"><div class="footer-copyright"><div class="container">© 2026 BarberShop</div></div></footer></body></html>''')

@csrf_exempt
def master_detail(request, master_id):
    master = get_object_or_404(Master, id=master_id)
    if request.method == "POST" and request.user.is_authenticated:
        Review.objects.create(master=master, user=request.user, rating=int(request.POST.get('rating')), text=request.POST.get('text'))
        avg = master.reviews.aggregate(Avg('rating'))['rating__avg']; master.rating = round(avg, 1) if avg else 5.0; master.reviews_count = master.reviews.count(); master.save()
        return redirect(f'/master/{master_id}/')
    revs = "".join([f'<li class="collection-item avatar"><i class="material-icons circle green">person</i><span class="title"><b>{r.user.username}</b></span><p class="orange-text">{"★"*r.rating}</p><p>{r.text}</p></li>' for r in master.reviews.all().order_by('-created_at')])
    form = f'''<div class="card-panel"><form method="POST"><label>Ваша оцінка:</label><select class="browser-default" name="rating" style="margin-bottom:15px"><option value="5">⭐⭐⭐⭐⭐ (5)</option><option value="4">⭐⭐⭐⭐ (4)</option><option value="3">⭐⭐⭐ (3)</option><option value="2">⭐⭐ (2)</option><option value="1">⭐ (1)</option></select><input name="text" required placeholder="Ваш відгук"><br><br><button class="btn green">Надіслати</button></form></div>''' if request.user.is_authenticated else '<div class="card-panel orange lighten-4 center">Увійдіть, щоб залишити відгук.</div>'
    return HttpResponse(f'''<!DOCTYPE html><html><head><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css"><link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet"></head><body class="grey lighten-5">
    <nav class="grey darken-4"><div class="container"><a href="/" class="brand-logo left"><i class="material-icons">arrow_back</i> Назад</a></div></nav><div class="container" style="margin-top:40px"><div class="row"><div class="col s12 m4"><img src="{master.photo_url}" class="responsive-img z-depth-3" style="border-radius:10px"></div><div class="col s12 m8"><h3>{master.name}</h3><h5>{master.specialty}</h5><h4 class="orange-text">★ {master.rating} <small class="grey-text">({master.reviews_count} відгуків)</small></h4><p class="flow-text">{master.bio}</p><br><a href="/book/" class="btn-large orange darken-3">Записатися до майстра</a></div></div><div class="row"><div class="col s12"><h4>Відгуки клієнтів</h4>{form}<ul class="collection">{revs}</ul></div></div></div></body></html>''')

@login_required
def profile_view(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-date_time')
    rows = "".join([f'<tr><td>{b.date_time.strftime("%d.%m.%Y %H:%M")}</td><td>{b.service.name}</td><td>{b.master.name}</td><td>{b.location.city}</td><td><span class="new badge green" data-badge-caption="Активно"></span></td></tr>' for b in bookings])
    if not rows: rows = "<tr><td colspan='5' class='center'>У вас ще немає записів.</td></tr>"
    return HttpResponse(f'''<!DOCTYPE html><html><head><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css"><link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet"></head><body class="grey lighten-4"><nav class="grey darken-4"><div class="container"><a href="/" class="brand-logo left"><i class="material-icons">arrow_back</i> На головну</a></div></nav><div class="container" style="margin-top:40px"><div class="card-panel"><h4><i class="material-icons left">account_circle</i> Кабінет користувача</h4><p><b>Логін:</b> {request.user.username}</p><p><b>З нами з:</b> {request.user.date_joined.strftime("%d.%m.%Y")}</p></div><div class="card"><div class="card-content"><span class="card-title">📅 Історія записів</span><table class="striped highlight responsive-table"><thead><tr><th>Дата</th><th>Послуга</th><th>Майстер</th><th>Місто</th><th>Статус</th></tr></thead><tbody>{rows}</tbody></table></div></div></div></body></html>''')

@csrf_exempt
@login_required
def book_service(request):
    if request.method == "POST":
        Booking.objects.create(user=request.user, service_id=request.POST.get('s'), master_id=request.POST.get('m'), location_id=request.POST.get('l'), date_time=request.POST.get('d'), phone=request.POST.get('phone'), wishes=request.POST.get('w'))
        return redirect('/profile/')

    l_ops = "".join([f'<option value="{x.id}">{x.city}, {x.address}</option>' for x in Location.objects.all()])
    s_ops = "".join([f'<option value="{x.id}">{x.name} - {x.price} грн</option>' for x in Service.objects.all()])
    m_ops = "".join([f'<option value="{x.id}">{x.name}</option>' for x in Master.objects.all()])

    return HttpResponse(f'''<!DOCTYPE html><html><head><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css"><link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet"><style>select{{display:block;margin-bottom:10px}}</style></head><body class="grey lighten-4"><div class="container" style="margin-top:20px"><div class="row"><div class="col s12 m8 offset-m2"><div class="card"><div class="card-content"><a href="/" class="btn-flat waves-effect" style="margin-bottom:10px; padding-left:0"><i class="material-icons left">arrow_back</i>Скасувати</a><h4>Запис</h4><form method="POST"><label>Послуга</label><select name="s">{s_ops}</select><label>Майстер</label><select name="m">{m_ops}</select><label>Локація</label><select name="l">{l_ops}</select><label>Телефон</label><input name="phone" required placeholder="+380..."><label>Час</label><input type="datetime-local" name="d" required><label>Побажання</label><textarea name="w" class="materialize-textarea"></textarea><br><br><button class="btn-large green waves-effect waves-light" style="width:100%">ПІДТВЕРДИТИ</button></form></div></div></div></div></div></body></html>''')

@csrf_exempt
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid(): user = form.save(); login(request, user); return redirect('/profile/')
    else: form = UserCreationForm()
    return HttpResponse(f'''<html><head><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css"><link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet"></head><body class="valign-wrapper" style="height:100vh; background:#eee"><div class="container"><div class="row"><div class="col s12 m6 offset-m3"><div class="card z-depth-4" style="padding:20px"><a href="/" class="btn-flat waves-effect" style="margin-bottom:10px; padding-left:0"><i class="material-icons left">arrow_back</i>На головну</a><h4 class="center">Реєстрація</h4><form method="POST">{form.as_p()}<br><button class="btn-large green waves-effect waves-light" style="width:100%">Створити акаунт</button></form><div class="clearfix"></div></div></div></div></div></body></html>''')

@csrf_exempt
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid(): user = form.get_user(); login(request, user); return redirect('/profile/')
    else: form = AuthenticationForm()
    return HttpResponse(f'''<html><head><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css"><link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet"></head><body class="valign-wrapper" style="height:100vh; background:#eee"><div class="container"><div class="row"><div class="col s12 m6 offset-m3"><div class="card z-depth-4" style="padding:20px"><a href="/" class="btn-flat waves-effect" style="margin-bottom:10px; padding-left:0"><i class="material-icons left">arrow_back</i>На головну</a><h4 class="center">Вхід</h4><form method="POST">{form.as_p()}<br><button class="btn-large orange waves-effect waves-light" style="width:100%">Увійти</button></form><div class="clearfix"></div><br><center><a href="/register/">Немає акаунту?</a></center></div></div></div></div></body></html>''')

def logout_view(request): logout(request); return redirect('/')
