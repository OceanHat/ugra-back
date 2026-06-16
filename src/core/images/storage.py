import shutil
from pathlib import Path
from typing import Optional, Tuple
from .processor import ImageProcessor
from .constants import (
    ITEM_IMAGES_DIR, ITEM_THUMBNAIL, ITEM_FULL,
    MAX_FILE_SIZE, ALLOWED_EXTENSIONS
)

class ImageStorageManager:
    """Управление хранилищем изображений"""
    
    @staticmethod
    def _ensure_dir(directory: Path) -> None:
        """Убедиться, что директория существует"""
        directory.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def save_item_image(
        file_bytes: bytes,
        original_filename: str
    ) -> str:
        """
        Сохранить изображение товара в оба формата (thumbnail + full)
        
        Args:
            file_bytes: Бинарные данные исходного изображения
            original_filename: Исходное имя файла
            
        Returns:
            Базовый путь (будет использоваться для обоих вариантов)
            
        Raises:
            ValueError: Если файл невалидный
        """
        # Валидация
        if len(file_bytes) > MAX_FILE_SIZE:
            raise ValueError(f"Файл слишком большой. Максимум: {MAX_FILE_SIZE / 1024 / 1024}MB")
        
        ext = Path(original_filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Недопустимый формат. Разрешены: {ALLOWED_EXTENSIONS}")
        
        if not ImageProcessor.validate_image(file_bytes):
            raise ValueError("Файл не является валидным изображением")
        
        # Генерируем имя
        safe_filename = ImageProcessor.get_image_filename(original_filename)
        base_name = Path(safe_filename).stem  # Без расширения
        
        # Создаем директории
        item_dir = ITEM_IMAGES_DIR / base_name
        ImageStorageManager._ensure_dir(item_dir)
        
        try:
            # Обрабатываем thumbnail
            thumbnail_data = ImageProcessor.process_image(file_bytes, ITEM_THUMBNAIL)
            thumbnail_path = item_dir / "thumbnail.webp"
            thumbnail_path.write_bytes(thumbnail_data)
            
            # Обрабатываем full version
            full_data = ImageProcessor.process_image(file_bytes, ITEM_FULL)
            full_path = item_dir / "full.webp"
            full_path.write_bytes(full_data)
            
            # Возвращаем базовый путь (без расширения и подпапки)
            return f"items/{base_name}"
            
        except Exception as e:
            # Удаляем созданную директорию при ошибке
            if item_dir.exists():
                shutil.rmtree(item_dir)
            raise Exception(f"Ошибка при сохранении изображения: {str(e)}")
    
    @staticmethod
    def get_image_path(
        picture_url: str,
        size: str = "full"  # "thumbnail" или "full"
    ) -> Optional[Path]:
        """
        Получить полный путь до изображения
        
        Args:
            picture_url: Базовый путь (например, "items/abc123")
            size: Размер изображения ("thumbnail" или "full")
            
        Returns:
            Полный путь до файла или None если файла нет
        """
        if not picture_url:
            return None
        
        # picture_url = "items/abc123" -> "storage/images/items/abc123/thumbnail.webp"
        file_path = Path(picture_url.replace("items", str(ITEM_IMAGES_DIR / ""), 1)) / f"{size}.webp"
        if file_path.exists():
            return file_path
        
        return None
    
    @staticmethod
    def delete_item_image(picture_url: str) -> bool:
        """
        Удалить оба варианта изображения
        
        Args:
            picture_url: Базовый путь (например, "items/abc123")
            
        Returns:
            True если успешно, False если файлов не было
        """
        if not picture_url:
            return False
        
        base_name = picture_url.split('/')[-1]
        item_dir = ITEM_IMAGES_DIR / base_name
        
        if item_dir.exists():
            try:
                shutil.rmtree(item_dir)
                return True
            except Exception as e:
                print(f"Ошибка при удалении изображения: {e}")
                return False
        
        return False
    
    @staticmethod
    def replace_item_image(
        old_picture_url: Optional[str],
        new_file_bytes: bytes,
        original_filename: str
    ) -> str:
        """
        Заменить изображение товара
        
        Args:
            old_picture_url: Старый путь (может быть None)
            new_file_bytes: Новые бинарные данные
            original_filename: Имя нового файла
            
        Returns:
            Новый путь изображения
        """
        # Сохраняем новое
        new_url = ImageStorageManager.save_item_image(new_file_bytes, original_filename)
        
        # Удаляем старое если было
        if old_picture_url:
            ImageStorageManager.delete_item_image(old_picture_url)
        
        return new_url
