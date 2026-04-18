from django.shortcuts import render
from artworks.models import Artwork, Tag

def explore_view(request):
    artworks = Artwork.objects.all().order_by('?') # Random for explore
    trending_tags = Tag.objects.all()
    return render(request, 'index.html', {
        'artworks': artworks, 
        'trending_tags': trending_tags,
        'section_title': 'Explore Collection',
        'section_tag': 'Random Discovery'
    })
