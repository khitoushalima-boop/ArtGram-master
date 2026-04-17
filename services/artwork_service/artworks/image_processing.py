from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
import os

class ArtworkImageProcessor:
    """
    High-quality image processing service for Artwork Service using Pillow
    Handles image optimization, thumbnail generation, and format conversion
    """
    
    @staticmethod
    def process_artwork_upload(artwork_image, artwork_instance):
        """
        Process uploaded artwork image with multiple sizes and optimizations
        
        Args:
            artwork_image: Uploaded image file
            artwork_instance: Artwork model instance
            
        Returns:
            dict: Processing results with generated file paths
        """
        if not artwork_image:
            return {
                'success': False,
                'error': 'No image provided'
            }
        
        try:
            # Open the uploaded image
            img = Image.open(artwork_image.path)
            
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Auto-orient the image based on EXIF data
            img = ImageOps.exif_transpose(img)
            
            # Generate multiple sizes for different use cases
            sizes = {
                'thumbnail': (300, 300),
                'medium': (800, 600),
                'large': (1200, 900),
                'original': img.size
            }
            
            processed_images = {}
            
            for size_name, dimensions in sizes.items():
                # Create a copy for each size
                img_copy = img.copy()
                
                # Only resize if it's not the original size
                if size_name != 'original':
                    img_copy.thumbnail(dimensions, Image.Resampling.LANCZOS)
                
                # Apply different optimizations based on size
                if size_name == 'thumbnail':
                    # Higher quality for thumbnails
                    quality = 90
                    optimize = True
                elif size_name == 'medium':
                    quality = 85
                    optimize = True
                elif size_name == 'large':
                    quality = 80
                    optimize = True
                else:
                    quality = 95
                    optimize = False
                
                # Save processed image
                buffer = BytesIO()
                
                # Determine format (prefer WebP for better compression)
                if artwork_image.name.lower().endswith(('.png', '.gif')):
                    format = 'PNG'
                else:
                    format = 'WEBP' if optimize else 'JPEG'
                
                img_copy.save(buffer, format=format, quality=quality, optimize=optimize)
                
                # Generate filename
                original_name = os.path.splitext(artwork_image.name)[0]
                if format == 'WEBP':
                    filename = f"{original_name}_{size_name}.webp"
                else:
                    filename = f"{original_name}_{size_name}.jpg"
                
                # Save to model field
                if size_name == 'thumbnail':
                    artwork_instance.thumbnail.save(filename, ContentFile(buffer.getvalue()), save=False)
                    processed_images['thumbnail'] = filename
                elif size_name == 'medium':
                    # Save medium version as additional field or replace original
                    artwork_instance.image.save(filename, ContentFile(buffer.getvalue()), save=False)
                    processed_images['medium'] = filename
                elif size_name == 'large':
                    # Save large version for high-quality display
                    processed_images['large'] = filename
                else:
                    processed_images['original'] = artwork_image.name
            
            return {
                'success': True,
                'processed_images': processed_images,
                'original_format': img.format,
                'original_size': img.size
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def generate_artwork_variants(artwork_image):
        """
        Generate multiple variants of artwork for different use cases
        
        Args:
            artwork_image: Uploaded image file
            
        Returns:
            dict: Generated variants with metadata
        """
        try:
            img = Image.open(artwork_image.path)
            
            # Get image metadata
            metadata = {
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'has_transparency': img.mode in ('RGBA', 'LA', 'P')
            }
            
            # Calculate aspect ratio
            width, height = img.size
            aspect_ratio = width / height if height > 0 else 1
            
            # Generate different crops
            variants = {
                'square': {
                    'size': (min(width, height), min(width, height)),
                    'aspect_ratio': 1.0
                },
                'landscape': {
                    'size': (width, int(width / aspect_ratio)) if aspect_ratio > 1 else (width, height),
                    'aspect_ratio': aspect_ratio
                },
                'portrait': {
                    'size': (int(height * aspect_ratio), height) if aspect_ratio < 1 else (width, height),
                    'aspect_ratio': aspect_ratio
                }
            }
            
            return {
                'success': True,
                'metadata': metadata,
                'variants': variants
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def optimize_for_web(artwork_image, max_width=1920, max_height=1080):
        """
        Optimize artwork for web display with size constraints
        
        Args:
            artwork_image: Uploaded image file
            max_width: Maximum width for web display
            max_height: Maximum height for web display
            
        Returns:
            dict: Optimization results
        """
        try:
            img = Image.open(artwork_image.path)
            
            # Calculate new dimensions maintaining aspect ratio
            width, height = img.size
            aspect_ratio = width / height if height > 0 else 1
            
            if width > max_width:
                new_width = max_width
                new_height = int(max_width / aspect_ratio)
            elif height > max_height:
                new_height = max_height
                new_width = int(max_height * aspect_ratio)
            else:
                new_width, new_height = width, height
            
            # Resize image
            img_resized = img.copy()
            img_resized.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save optimized version
            buffer = BytesIO()
            img_resized.save(buffer, format='WEBP', quality=85, optimize=True, method=6)
            
            original_name = os.path.splitext(artwork_image.name)[0]
            filename = f"{original_name}_optimized.webp"
            
            return {
                'success': True,
                'filename': filename,
                'original_size': (width, height),
                'optimized_size': (new_width, new_height),
                'compression_ratio': len(buffer.getvalue()) / len(artwork_image.read()) if hasattr(artwork_image, 'read') else 1
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
