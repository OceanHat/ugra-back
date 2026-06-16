import io
from pathlib import Path
from PIL import Image
from .constants import ImageSize, ALLOWED_EXTENSIONS, MAX_FILE_SIZE

class ImageProcessor:
    """Обработка и оптимизация изображений"""
    
    @staticmethod
    def validate_image(file_bytes: bytes) -> bool:
        """Проверить, что это валидное изображение"""
        try:
            img = Image.open(io.BytesIO(file_bytes))
            img.verify()
            return True
        except Exception:
            return False
    
    @staticmethod
    def process_image(
        file_bytes: bytes,
        target_size: ImageSize
    ) -> bytes:
        """
        Обработать изображение: resize и конвертация в webp
        
        Args:
            file_bytes: Бинарные данные изображения
            target_size: Целевой размер и качество
            
        Returns:
            Обработанное изображение в формате webp
        """
        img = Image.open(io.BytesIO(file_bytes))
        
        # Конвертируем RGBA в RGB если нужно
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Resize с сохранением aspect ratio
        img.thumbnail((target_size.width, target_size.height), Image.Resampling.LANCZOS)
        
        # Конвертируем в webp
        output = io.BytesIO()
        img.save(output, format='WEBP', quality=target_size.quality, method=6)
        output.seek(0)
        
        return output.getvalue()
    
    @staticmethod
    def get_image_filename(original_name: str) -> str:
        """Генерировать безопасное имя файла"""
        import uuid
        ext = Path(original_name).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            ext = '.jpg'
        return f"{uuid.uuid4()}{ext}"
