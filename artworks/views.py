from django.shortcuts import render, get_object_or_404
from .models import Artwork, Tag

def home(request):
    artworks = Artwork.objects.all().order_by('-created_at')[:6]
    trending_tags = Tag.objects.all()[:10]
    
    context = {
        'artworks': artworks,
        'trending_tags': trending_tags,
    }
    return render(request, 'index.html', context)

def artwork_detail(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk)
    return render(request, 'artwork_detail.html', {'artwork': artwork})

def search_view(request):
    query = request.GET.get('q')
    artworks = Artwork.objects.none()
    if query:
        artworks = Artwork.objects.filter(title__icontains=query) | \
                   Artwork.objects.filter(description__icontains=query) | \
                   Artwork.objects.filter(user__username__icontains=query) | \
                   Artwork.objects.filter(tags__name__icontains=query)
        artworks = artworks.distinct()
        
    trending_tags = Tag.objects.all()[:10]
    return render(request, 'index.html', {
        'artworks': artworks,
        'trending_tags': trending_tags,
        'section_title': f'Search Results for "{query}"' if query else 'Search Collection',
        'section_tag': f'{artworks.count()} works found' if query else 'Start discovery'
    })
