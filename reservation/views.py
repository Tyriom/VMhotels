from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from hotels.models import Room, Hotel
from .models import Reservation
from .forms import ReservationForm
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.views import generic
# Create your views here.

##NON E' UNA VIEW.
def check_res(newres, room):
	for res in Reservation.objects.filter(room = room, is_active=True):
		if (res == newres):
			continue
		if (newres.idate >= res.idate) and (newres.idate <= res.fdate):
			return False
		elif (newres.fdate >= res.idate) and (newres.fdate <= res.fdate):
			return False
		elif (newres.idate >= res.idate) and (newres.fdate <= res.fdate):
			return False
		elif (newres.idate <= res.idate) and (newres.fdate >= res.fdate):
			return False
	return True
	
def update_state_res(room):
	rlist = room.reservation_set.filter(is_active = False).order_by('updated')
	for non_active_res in rlist:
		if check_res(non_active_res, room):
			non_active_res.is_active = True
			non_active_res.save()
			#NOTIFICA

@login_required
@permission_required('reservation.add_reservation')
def add_reservation(request, hotel_id, room_id):
	h = get_object_or_404(Hotel, pk=hotel_id)
	r = get_object_or_404(Room, pk=room_id)
	if h.pk != r.hotel.pk:
		return HttpResponseForbidden("Non esiste questa stanza in questo Hotel")
	if 'Ok' in request.POST:
		form = ReservationForm(request.POST)
		if form.is_valid():
			newres = form.save(commit=False)
			newres.user = request.user
			newres.room = r
			if check_res(newres, r):
				newres.is_active = True
				newres.save()
				return HttpResponseRedirect(reverse('portal:personal'))
			else:
				newres.is_active = False
				newres.save()
				return render(request, 'reservation/inqueue.html')
	elif request.method == 'GET':
		form = ReservationForm()
	return render(request, 'reservation/addreservation.html', {'form': form, 'hotel': h, 'room': r})

@login_required
def reservation_detail(request, reservation_id):
	res = get_object_or_404(Reservation, pk=reservation_id)
	if request.user == res.user:
		return render(request, 'reservation/reservation_detail.html', {'reservation': res})
	return HttpResponseForbidden("This reservation is not yours")
	
@login_required
@permission_required('reservation.change_reservation')
def edit_reservation(request, reservation_id):
	res = get_object_or_404(Reservation, pk=reservation_id)
	r = get_object_or_404(Room, pk=res.room.pk)
	h = get_object_or_404(Hotel, pk=r.hotel.pk)
	if res.user != request.user: ##Se l'utente della sessione non e' il titolare della prenotazione
		return HttpResponseForbidden("This reservation is not yours.")
	if 'Ok' in request.POST:
		form = ReservationForm(request.POST, instance = res)
		if form.is_valid():
			form.save(commit=False)
			if check_res(res, r):
				res.is_active = True
				res.save()
				update_state_res(r)
				return HttpResponseRedirect(reverse('reservation:reservation_detail', args=(res.id,)))
			else:
				res.is_active = False
				res.save()
				update_state_res(r)
				return render(request, 'reservation/inqueue.html')
	elif request.method == 'GET': ##caso GET
		form = ReservationForm(instance = res)
	return render(request, 'reservation/editreservation.html', {'form': form, 'hotel': h, 'room': r, 'reservation':res,})
	
@login_required
@permission_required('reservation.delete_reservation')
def delete_reservation(request, reservation_id):
	res = get_object_or_404(Reservation, pk=reservation_id)
	r = get_object_or_404(Room, pk=res.room.pk)
	h = get_object_or_404(Hotel, pk=r.hotel.pk)
	if res.user != request.user: ##Se l'utente della sessione non e' il titolare della prenotazione
		return HttpResponseForbidden("This reservation is not yours.")
	if 'Ok' in request.POST:
		Reservation.objects.filter(id=res.id).delete()
		update_state_res(r)
		return HttpResponseRedirect(reverse('portal:personal'))
	return render(request, 'reservation/deletereservation.html', {'hotel': h, 'room': r, 'reservation':res,})
