import os
import django
import requests
from django.core.files.base import ContentFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artgram.settings')
django.setup()

from artworks.models import Artwork

def populate():
    if Artwork.objects.exists():
        print("Artworks already exist. Skipping population.")
        return

    artworks_data = [
        {
            "title": "La Lumière du Soir",
            "description": "A meditation on the quality of evening light.",
            "user_id": 1,
            "url": "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?w=800&h=600&fit=crop"
        },
        {
            "title": "Threshold",
            "description": "Doorways as metaphors for transition.",
            "user_id": 2,
            "url": "https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=800&h=600&fit=crop"
        },
        {
            "title": "Archive No. 7",
            "description": "Fragments of letters and botanicals.",
            "user_id": 1,
            "url": "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=800&h=600&fit=crop"
        },
        {
            "title": "Still II",
            "description": "The second in a series examining domestic stillness.",
            "user_id": 1,
            "url": "https://images.unsplash.com/photo-1603126857599-f6e157fa2fe6?w=800&h=600&fit=crop"
        },
        {
            "title": "Dusk Protocol",
            "description": "A generative work exploring the visual language of dusk.",
            "user_id": 3,
            "url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=600&fit=crop"
        },
        {
            "title": "Remnant",
            "description": "A lone chair on an empty stage.",
            "user_id": 2,
            "url": "https://images.unsplash.com/photo-1501084817091-a4f3d1d19e07?w=800&h=600&fit=crop"
        },
        {
            "title": "Cartography of Sleep",
            "description": "Inspired by sleep studies and dream states.",
            "user_id": 4,
            "url": "https://images.unsplash.com/photo-1547826039-bfc35e0f1ea8?w=800&h=600&fit=crop"
        },
        {
            "title": "Form Study V",
            "description": "Geometric form and organic improvisation.",
            "user_id": 3,
            "url": "https://images.unsplash.com/photo-1622737133809-d95047b9e673?w=800&h=600&fit=crop"
        },
        {
            "title": "Grey Water",
            "description": "Layers built up and scraped back.",
            "user_id": 4,
            "url": "https://images.unsplash.com/photo-1536924940846-227afb31e2a5?w=800&h=600&fit=crop"
        }
    ]

    for data in artworks_data:
        try:
            print(f"Downloading {data['title']}...")
            response = requests.get(data['url'])
            if response.status_code == 200:
                filename = data['url'].split('/')[-1].split('?')[0] + ".jpg"
                artwork = Artwork(
                    title=data['title'],
                    description=data['description'],
                    user_id=data['user_id']
                )
                artwork.image.save(filename, ContentFile(response.content), save=True)
                print(f"Created {data['title']}")
        except Exception as e:
            print(f"Error creating {data['title']}: {e}")

if __name__ == "__main__":
    populate()
