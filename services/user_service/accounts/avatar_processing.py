from PIL import Image, ImageOps
import io
import os
from django.core.files.base import ContentFile
from django.conf import settings

class AvatarProcessor:
    """High-resolution avatar processing service using Pillow"""
    
    @staticmethod
    def process_avatar(image_field, thumbnail_field, sizes=[(200, 200), (100, 100), (50, 50)]):
        """
        Process uploaded avatar image with multiple sizes and optimizations
        
        Args:
            image_field: Original ImageField
            thumbnail_field: Thumbnail ImageField to store processed image
            sizes: List of (width, height) tuples for different sizes
        """
        if not image_field:
            return
        
        try:
            # Open the uploaded image
            img = Image.open(image_field)
            
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Auto-orient the image based on EXIF data
            img = ImageOps.exif_transpose(img)
            
            # Process for different sizes
            for size in sizes:
                # Create thumbnail with high-quality resampling
                img_copy = img.copy()
                img_copy.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Crop to square if needed
                if img_copy.size[0] != img_copy.size[1]:
                    img_copy = ImageOps.fit(img_copy, size, Image.Resampling.LANCZOS, centering=(0.5, 0.5))
                
                # Apply subtle sharpening
                from PIL import ImageFilter
                img_copy = img_copy.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))
                
                # Save processed image
                buffer = io.BytesIO()
                
                # Optimize for web
                if img_copy.size[0] <= 100:
                    quality = 85
                else:
                    quality = 90
                
                img_copy.save(buffer, format='JPEG', quality=quality, optimize=True, progressive=True)
                
                # Save to thumbnail field (using largest size)
                if size == max(sizes):
                    thumbnail_field.save(
                        f"avatar_{img_copy.size[0]}x{img_copy.size[1]}.jpg",
                        ContentFile(buffer.getvalue())
                    )
            
            return True
            
        except Exception as e:
            print(f"Error processing avatar: {e}")
            return False
    
    @staticmethod
    def process_avatar_update(new_avatar, old_avatar_thumbnail=None):
        """
        Process avatar update with old file cleanup.
        
        Args:
            new_avatar: New uploaded image file
            old_avatar_thumbnail: Old thumbnail file to be cleaned up
            
        Returns:
            bool: Success status
        """
        if not new_avatar:
            return True
            
        try:
            # Open the new avatar
            img = Image.open(new_avatar)
            
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Auto-orient the image based on EXIF data
            img = ImageOps.exif_transpose(img)
            
            # Create standard sizes for profile
            sizes = [(200, 200), (100, 100), (50, 50)]
            processed_images = {}
            
            for size in sizes:
                # Create thumbnail with high-quality resampling
                img_copy = img.copy()
                img_copy.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Crop to square if needed
                if img_copy.size[0] != img_copy.size[1]:
                    img_copy = ImageOps.fit(img_copy, size, Image.Resampling.LANCZOS, centering=(0.5, 0.5))
                
                # Apply subtle sharpening
                from PIL import ImageFilter
                img_copy = img_copy.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))
                
                # Save processed image to buffer
                buffer = io.BytesIO()
                img_copy.save(buffer, format='JPEG', quality=90, optimize=True, progressive=True)
                
                processed_images[f"{size[0]}x{size[1]}"] = buffer.getvalue()
            
            # Clean up old avatar thumbnail if it exists
            if old_avatar_thumbnail and hasattr(old_avatar_thumbnail, 'path'):
                try:
                    old_avatar_thumbnail.delete(save=False)
                    print(f"Deleted old avatar thumbnail: {old_avatar_thumbnail.path}")
                except Exception as cleanup_error:
                    print(f"Failed to delete old avatar: {cleanup_error}")
            
            return {
                'success': True,
                'processed_images': processed_images,
                'sizes': sizes
            }
            
        except Exception as e:
            print(f"Error processing avatar update: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def create_default_avatar(username, size=200):
        """
        Create a default avatar with user's initial
        
        Args:
            username: User's username
            size: Image size (square)
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create image with gradient background
            img = Image.new('RGB', (size, size), color='#6366f1')
            draw = ImageDraw.Draw(img)
            
            # Add subtle gradient effect
            for i in range(size):
                alpha = int(255 * (1 - i / size))
                color = (99, 102, 241, alpha) if i < size // 2 else (99, 102, 241, 255 - alpha)
                draw.line([(0, i), (size, i)], fill=color[:3])
            
            # Get first letter
            initial = username[0].upper() if username else 'U'
            
            # Try to use a nice font, fallback to default
            try:
                font_size = size // 3
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # Calculate text position
            bbox = draw.textbbox((0, 0), initial, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (size - text_width) // 2
            y = (size - text_height) // 2
            
            # Draw text with shadow
            draw.text((x + 2, y + 2), initial, fill=(0, 0, 0, 50), font=font)
            draw.text((x, y), initial, fill=(255, 255, 255), font=font)
            
            # Save to buffer
            buffer = io.BytesIO()
            img.save(buffer, format='PNG', optimize=True)
            
            return ContentFile(buffer.getvalue(), f"default_avatar_{username}.png")
            
        except Exception as e:
            print(f"Error creating default avatar: {e}")
            return None
    
    @staticmethod
    def optimize_avatar_size(image_path, max_size_mb=2):
        """
        Optimize avatar file size while maintaining quality
        
        Args:
            image_path: Path to the image file
            max_size_mb: Maximum file size in MB
        """
        try:
            img = Image.open(image_path)
            original_size = os.path.getsize(image_path) / (1024 * 1024)  # Size in MB
            
            if original_size <= max_size_mb:
                return True  # Already within size limits
            
            # Reduce quality progressively until size is acceptable
            quality = 95
            while quality > 50:
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=quality, optimize=True, progressive=True)
                
                file_size = len(buffer.getvalue()) / (1024 * 1024)
                if file_size <= max_size_mb:
                    # Save the optimized version
                    with open(image_path, 'wb') as f:
                        f.write(buffer.getvalue())
                    return True
                
                quality -= 5
            
            # If still too large, resize the image
            max_dimension = 800
            if max(img.size) > max_dimension:
                img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85, optimize=True, progressive=True)
                
                with open(image_path, 'wb') as f:
                    f.write(buffer.getvalue())
            
            return True
            
        except Exception as e:
            print(f"Error optimizing avatar size: {e}")
            return False
