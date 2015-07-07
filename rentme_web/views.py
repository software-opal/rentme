import django.http
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from rentme_web import models, api

# Create your views here.

def load_all_locality(request):
    api.load_trademe_locality_information()
    return redirect('all-localities')

def list_all_locality(request):
    localities = models.TradeMeLocality.objects.order_by('name').all()
    count = models.TradeMeLocality.objects.count()
    context = {'localities': localities, 'c': count}
    return render(request, 'rentme/locality_all.html', context)

def load_search_rentals(request):
    kwargs = {key: val for key, val in request.GET.items()}
    x = api.search_rentals(**kwargs)
    return django.http.response.HttpResponse("Loaded " + str(len(x)) + " "
                                                                   "properties")

def load_rental(request, id):
    x = api.load_rental(id)
    return django.http.response.HttpResponse("Loaded property")

def all_rentals(request):
    context = {}
    filters = [
        Q(rent_per_week__lt=475),
        Q(rent_per_week__gt=300),
        Q(bedrooms__gte=2),
    ]
    if not request.GET.get('all', None):
        filters.append(Q(rating__isnull=True) | Q(rating__rating__gte=1))
    ls_all = models.TradeMeListing.objects.filter(*filters)
    context['listing_list'] = ls_all

    return render(request, 'rentme/listings_all.html', context)

def one_rental(request, id):
    listing = get_object_or_404(models.TradeMeListing, id=id)
    context = {'listing': listing}
    same_loc_listings = set(listing.location.trademelisting_set.all())
    if listing.location.accuracy in (1, 3):
        ##  Street or Address accuracy level
        context['similar_location_listings'] = same_loc_listings
        context['similar_location_photos'] = models.photos_cleanup([
            photo for ls in same_loc_listings for photo in ls.all_photos
        ])
    return render(request, 'rentme/listing_single.html', context)

def review_rental(request, id, rating):
    rating = rating.lower()
    listing = get_object_or_404(models.TradeMeListing, id=id)
    if rating in models.PropertyRating.MAPPING:
        rating = models.PropertyRating.MAPPING[rating]
        pr_rating, _ = models.PropertyRating.objects.get_or_create(
            defaults={'rating': rating},
            property=listing
        )
        pr_rating.rating = rating
        pr_rating.save()
    return redirect('rentals/all')
