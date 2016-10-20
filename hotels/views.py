from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.views import generic
from .models import Room, Hotel
from .forms import HotelForm, RoomForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse

# Create your views here.
class HotelDetailView(generic.DetailView):
	model = Hotel
	template_name = 'hotels/hotel_detail.html'
	
def room_detail(request, hotel_id, room_id):
	hotel = get_object_or_404(Hotel, pk=hotel_id)
	room = get_object_or_404(Room, pk=room_id)
	services = hotel.services.all()
	context = {'hotel': hotel, 'room': room, 'services': services}
	return render(request, 'hotels/room_detail.html', context)

@login_required
@permission_required('hotels.add_hotel')
def create_hotel(request):
	if request.method == 'POST':
		form = HotelForm(request.POST, request.FILES)
		if form.is_valid():
			h = form.save(commit=False)
			h.user = request.user
			h.save() ##FARE CON TRY-CATCH
			services = form.cleaned_data['services']
			for service in services:
				h.services.add(service)
			return HttpResponseRedirect(reverse('hotels:hotel_detail', args=(h.pk,)))
	else:
		form = HotelForm()
	return render(request, 'hotels/inserthotel.html', {'form': form,})

@login_required
@permission_required('hotels.add_room')
def create_room(request, hotel_id):
	h = get_object_or_404(Hotel, pk=hotel_id)
	if request.user == h.user:
		if request.method == 'POST':
			form = RoomForm(request.POST, request.FILES)
			if form.is_valid():
				r = form.save(commit = False)
				r.hotel = h
				r.save() ##FARE CON TRY-CATCH
				return HttpResponseRedirect(reverse('hotels:room_detail', args=(h.pk, r.pk,)))
		else: #caso GET
			form = RoomForm()
		return render(request, 'hotels/insertroom.html', {'form': form,})
	#Caso di user non uguale
	return HttpResponseForbidden("You're not the owner of this Hotel.")
			
@login_required
@permission_required('hotels.change_hotel')
def edit_hotel(request, hotel_id):
	h = get_object_or_404(Hotel, pk=hotel_id)
	if request.user != h.user: ##Se l'utente della sessione non e' il proprietario dell'hotel
		return HttpResponseForbidden("You're not the owner of this Hotel.")
	if 'Ok' in request.POST:
		form = HotelForm(request.POST, request.FILES, instance = h)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('hotels:hotel_detail', args=(h.pk,)))
	elif request.method == 'GET': ##caso GET
		form = HotelForm(instance = h)
	return render(request, 'hotels/edithotel.html', {'form': form, 'hotel': h}) 
    	
@login_required
@permission_required('hotels.change_room')	
def edit_room(request, hotel_id, room_id):
	h = get_object_or_404(Hotel, pk=hotel_id)
	r = get_object_or_404(Room, pk=room_id)
	if h.user != request.user: ##Se l'utente della sessione non e' il proprietario dell'hotel
		return HttpResponseForbidden("You're not the owner of this Hotel.")
	if h.pk == r.hotel.pk: ##Se la stanza e' di questo hotel
		if 'Ok' in request.POST:
			form = RoomForm(request.POST, request.FILES, instance = r)
			if form.is_valid():
				form.save()
				return HttpResponseRedirect(reverse('hotels:room_detail', args=(h.pk, r.pk,)))
		elif request.method == 'GET': ##caso GET
			form = RoomForm(instance = r)
		return render(request, 'hotels/editroom.html', {'form': form, 'hotel': h, 'room': r})
	return HttpResponseForbidden("This Room doesn't exist in this Hotel.")
