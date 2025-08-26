from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
import time
import os
from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete
from django.dispatch import receiver

User = get_user_model()

class Direction_of_business(models.Model):
    # направление бизнеса (глобальные)
    name = models.CharField(max_length=100, verbose_name="Название бизнеса")
    description = models.TextField(blank=True, verbose_name="Описание")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Направления бизнеса"
        verbose_name_plural = "Направления бизнеса"


class Direction(models.Model):
    # направления (локальные)
    name = models.CharField(max_length=100, verbose_name="Название рубрики")
    description = models.TextField(blank=True, verbose_name="Описание")
    global_section = models.ForeignKey(Direction_of_business, on_delete=models.CASCADE,
                                       verbose_name="Направление бизнеса")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Направление"
        verbose_name_plural = "Направления"


class Section(models.Model):
    # рубрики
    name = models.CharField(max_length=100, verbose_name="Название рубрики")
    description = models.TextField(blank=True, verbose_name="Описание")
    global_section = models.ForeignKey(Direction_of_business, on_delete=models.CASCADE,
                                       verbose_name="Направление бизнеса")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Рубрика"
        verbose_name_plural = "Рубрики"


class Doc_class(models.Model):
    # типы документов
    name = models.CharField(max_length=100, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тип документа"
        verbose_name_plural = "Типы документов"


def document_upload_to(instance, filename):
    return f'documents/{int(time.time())}_{filename}'


class Document(models.Model):
    # документ
    STATUS_CHOICES = [
        ('active', 'Действующая редакция'),
        ('obsolete', 'Утратил силу'),
    ]

    title = models.CharField(max_length=255, verbose_name="Название документа")
    file = models.FileField(upload_to='documents/', verbose_name="Файл документа", blank=True, null=True)
    word_file = models.FileField(upload_to='documents/word/', verbose_name="Исходный Word-файл", blank=True, null=True, 
                                help_text="Необязательное поле. Исходный Word-файл для редактирования.")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    version_date = models.DateField(verbose_name="Дата редакции", null=True, blank=True)
    global_section = models.ForeignKey(Direction_of_business, on_delete=models.CASCADE, verbose_name="Направление бизнеса")
    section = models.ForeignKey(Direction, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Направление", default='none')
    category = models.ForeignKey(Section, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Рубрика")
    subcategory = models.ForeignKey(Doc_class, on_delete=models.CASCADE, verbose_name="Тип документа")
    is_template = models.BooleanField(default=False, verbose_name="Это шаблон")
    description = CKEditor5Field(verbose_name='Полное описание', config_name='extends', blank=True, null=True)
    # Флаг, что документ уже определён как "Смешанный контент" хотя бы один раз
    is_mixed = models.BooleanField(default=False, editable=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"

    def get_absolute_url(self):
        return reverse('knowledge_base:document_detail', args=[self.id])

    def get_display_type(self):
        """
        Определяет тип отображения документа на основе прикрепленных файлов и параметров
        """
        # Если документ уже помечен как mixed — всегда возвращаем mixed
        if self.is_mixed:
            return 'mixed_content'

        # Сначала проверяем специфичные типы файлов (приоритет выше description)
        
        # 1. Презентация (PPTX) - всегда презентация, независимо от описания
        if self.file and self.file.name.lower().endswith('.pptx'):
            return 'presentation'
        
        # 2. Word-шаблон (DOCX + is_template=True)
        if self.file and self.file.name.lower().endswith('.docx') and self.is_template:
            return 'word_template'
        
        # 3. PDF-документ (файл PDF, но не смешанный тип)
        if self.file and self.file.name.lower().endswith('.pdf'):
            # Если есть и описание, и PDF - проверяем есть ли дополнительные вложения
            if self.description and self.attachments.exists():
                return 'mixed_content'  # PDF + описание + вложения = смешанный
            else:
                return 'pdf_document'   # Просто PDF (с описанием или без)

        # 4. Смешанный тип (есть description И есть вложения, но нет основного файла)
        if self.description and self.attachments.exists():
            if not self.is_mixed:  # фиксируем флаг один раз
                self.is_mixed = True
                self.save(update_fields=['is_mixed'])
            return 'mixed_content'
        
        # 5. Только текстовая информация (есть только description, без файлов)
        if self.description and not self.file and not self.attachments.exists():
            return 'text_only'
        
        # 6. Документ без описания и вложений (только основной файл)
        if self.file and not self.description and not self.attachments.exists():
            return 'pdf_document'  # fallback для любых файлов без описания

        # Fallback: если ничего нет
            return 'text_only'
    
    def is_readable_pdf(self):
        """
        Определяет, является ли PDF читаемым (содержит текст)
        Теперь PDF.js обрабатывает все PDF
        """
        if not self.file or not self.file.name.lower().endswith('.pdf'):
            return False
        
        # PDF.js обрабатывает все PDF, считаем все читаемыми
        return True

    @property
    def latest_version(self):
        return self.versions.order_by('-version_number').first()

    @property
    def current_version(self):
        """
        Возвращает актуальную редакцию документа по самой новой version_date.
        """
        # Получаем версию с самой новой датой редакции
        latest_version = self.versions.filter(version_date__isnull=False).order_by('-version_date').first()
        
        # Если нет версий с датой, возвращаем None (используется основной файл)
        if not latest_version:
            return None
            
        # Если нет основного файла, возвращаем версию
        if not self.file:
            return latest_version
            
        # Сравниваем даты
        main_file_date = self.version_date or self.updated_at.date()
        version_date = latest_version.version_date
        
        # Если версия новее основного файла по дате редакции, возвращаем версию
        if version_date > main_file_date:
            return latest_version
        else:
            # Иначе основной файл актуальнее
            return None

    @property
    def all_versions(self):
        """
        Возвращает все версии документа, включая основной файл как версию 0
        """
        versions = list(self.versions.all())
        
        # Добавляем основной файл как версию 0, если он есть
        if self.file:
            from django.utils import timezone
            main_version = type('MainVersion', (), {
                'id': 'main',
                'version_number': 0,
                'file': self.file,
                'version_date': self.version_date,
                'uploaded_at': self.updated_at,
                'comment': 'Основной документ',
                'file_type': 'pdf' if self.file.name.lower().endswith('.pdf') else 'docx',
                'is_main': True
            })()
            versions.insert(0, main_version)
        
        return versions

    def save(self, *args, **kwargs):
        # Проверяем, есть ли уже версии у документа
        if self.pk:  # Документ уже существует
            existing_versions = self.versions.count()
            if existing_versions == 0 and self.file:
                # Если нет версий, но есть основной файл - создаем версию из него
                super().save(*args, **kwargs)
                self._create_main_file_version()
            else:
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
    
    def _create_main_file_version(self):
        """Создает версию из основного файла документа"""
        if self.file and not self.versions.exists():
            DocumentVersion.objects.create(
                document=self,
                file=self.file,
                version_number=1,
                version_date=self.version_date or self.updated_at.date(),
                comment="Исходная версия документа",
                file_type='pdf' if self.file.name.lower().endswith('.pdf') else 'docx'
            )


class DocumentVersion(models.Model):
    document = models.ForeignKey(Document, related_name='versions', on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/versions/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    version_number = models.PositiveIntegerField()
    comment = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    file_type = models.CharField(
        max_length=10,
        choices=[('pdf', 'PDF'), ('docx', 'Word'), ('xlsx', 'Excel')],
        default='pdf'
    )
    word_file = models.FileField(upload_to='documents/versions/word/', blank=True, null=True, verbose_name='Исходный Word-файл')
    version_date = models.DateField("Дата редакции", null=True, blank=True)

    class Meta:
        unique_together = ('document', 'version_number')
        ordering = ['-version_date', '-uploaded_at']

    def __str__(self):
        return f"{self.document.title} v{self.version_number}"


class PresentationSlide(models.Model):
    document = models.ForeignKey(Document, related_name='slides', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='presentations/slides/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class DocumentAttachment(models.Model):
    """Файл-вложение к mixed-content документу (может быть любой тип)."""
    document = models.ForeignKey(Document, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Вложение'
        verbose_name_plural = 'Вложения'

    def __str__(self):
        return f"{self.document.title} | {self.file.name.split('/')[-1]}"
    
    def filename(self):
        """Returns just the filename without path"""
        return self.file.name.split('/')[-1]


# Автоудаление файлов при удалении моделей

@receiver(post_delete, sender=Document)
def delete_document_files(sender, instance, **kwargs):
    """Удаляет файлы документа при удалении записи"""
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
    if instance.word_file:
        if os.path.isfile(instance.word_file.path):
            os.remove(instance.word_file.path)


@receiver(post_delete, sender=DocumentVersion)
def delete_version_files(sender, instance, **kwargs):
    """Удаляет файлы версии при удалении записи"""
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
    if instance.word_file:
        if os.path.isfile(instance.word_file.path):
            os.remove(instance.word_file.path)


@receiver(post_delete, sender=DocumentAttachment)
def delete_attachment_files(sender, instance, **kwargs):
    """Удаляет файлы вложений при удалении записи"""
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(post_delete, sender=PresentationSlide)
def delete_slide_files(sender, instance, **kwargs):
    """Удаляет файлы слайдов при удалении записи"""
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)