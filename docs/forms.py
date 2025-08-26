from django import forms
from .models import Doc_class, Section, Direction, Direction_of_business, Document, DocumentVersion, PresentationSlide
from django_ckeditor_5.widgets import CKEditor5Widget
import zipfile
from django.core.files.base import ContentFile
import re


# --- helpers ---


class MultiFileInput(forms.FileInput):
    """FileInput that allows selection of multiple files."""
    allow_multiple_selected = True


class SearchForm(forms.Form):
    """
    Форма для поиска
    """
    query = forms.CharField(
        max_length=200,  # указываем максисалью длину
        required=False,  # указываем, что поле не обязательно к заполнению
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Поиск...',  # указываем плейсхолдер
                "class": "form-control search-field"  # указываем bootstrap класс
            }))
    directional = forms.CharField(widget=forms.HiddenInput(), required=False)


class DocumentForm(forms.ModelForm):
    """Базовая форма для всех типов документов"""
    title = forms.CharField(label='Название', required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    global_section = forms.ModelChoiceField(label='Направление бизнеса',
                                            required=True,
                                            empty_label='Выбери направление бизнеса',
                                            queryset=Direction_of_business.objects.all(),
                                            widget=forms.Select(attrs={"class": "form-control"}),
                                            )
    section = forms.ModelChoiceField(label='Направление',
                                     required=False,
                                     empty_label='Выбери направление',
                                     queryset=Direction.objects.all(),
                                     widget=forms.Select(attrs={"class": "form-control"}),
                                     )
    category = forms.ModelChoiceField(label='Рубрика',
                                      required=True,
                                      empty_label='Выбери рубрику',
                                      queryset=Section.objects.all(),
                                      widget=forms.Select(attrs={"class": "form-control"}),
                                      )
    subcategory = forms.ModelChoiceField(label='Тип документа',
                                         required=True,
                                         empty_label='Выбери тип документа',
                                         queryset=Doc_class.objects.all(),
                                         widget=forms.Select(attrs={"class": "form-control"}),
                                         )

    class Meta:
        model = Document
        fields = ['title', 'global_section', 'section', 'category', 'subcategory']


class DocumentPDFForm(DocumentForm):
    """Форма для PDF документов с версионированием"""
    file = forms.FileField(label='Файл документа', required=True, widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'accept': '.pdf'
        }
    ))
    word_file = forms.FileField(label='Исходный Word-файл', required=False, widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'accept': '.docx, .doc',
            'title': 'Необязательное поле. Исходный Word-файл для редактирования.'
        }
    ))
    version_date = forms.DateField(label='Дата редакции:',
                                   widget=forms.DateInput(format='%Y-%m-%d',
                                                          attrs={"class": "form-control",
                                                                 "type": "date"}),
                                   initial=None,
                                   required=False)

    class Meta:
        model = Document
        fields = ['title', 'global_section', 'section', 'category', 'subcategory', 'file', 'word_file', 'version_date']


class DocumentInfoForm(DocumentForm):
    """Форма для текстовой информации"""
    description = forms.CharField(label='Описание:',
                                  widget=CKEditor5Widget(
                                      attrs={"class": "django_ckeditor_5"}, config_name="extends"),
                                  required=True)

    class Meta:
        model = Document
        fields = ['title', 'global_section', 'section', 'category', 'subcategory', 'description']


class DocumentFileForm(DocumentForm):
    """Форма для mixed_content: описание + несколько вложений"""

    description = forms.CharField(
        label='Описание:',
        widget=CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="extends"),
        required=False
    )

    class Meta:
        model = Document
        fields = ['title', 'global_section', 'section', 'category', 'subcategory', 'description']


class DocumentTemplateForm(DocumentForm):
    """Форма для Word шаблонов"""
    file = forms.FileField(label='Word-шаблон', required=True, widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'accept': '.docx'
        }
    ))

    class Meta:
        model = Document
        fields = ['title', 'global_section', 'section', 'category', 'subcategory', 'file']


class DocumentPresentationForm(DocumentForm):
    """Форма для презентаций"""
    file = forms.FileField(label='Презентация', required=True, widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'accept': '.pptx'
        }
    ))
    description = forms.CharField(label='Описание:',
                                  widget=CKEditor5Widget(
                                      attrs={"class": "django_ckeditor_5"}, config_name="extends"),
                                  required=False)
    slides_zip = forms.FileField(label='Архив с PNG-слайдами', required=True, widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Document
        fields = ['title', 'global_section', 'section', 'category', 'subcategory', 'file', 'description', 'slides_zip']

    def save(self, commit=True):
        instance = super().save(commit)
        # Только если загружен новый pptx — обновляем
        if self.cleaned_data.get('file'):
            instance.file = self.cleaned_data['file']
        # Только если загружен новый архив — обновляем слайды
        zip_file = self.cleaned_data.get('slides_zip')
        if zip_file:
            slide_form = SlideZipUploadForm(files={'zip_file': zip_file})
            if slide_form.is_valid():
                slide_form.save(instance)
        return instance


class DocumentVersionForm(forms.ModelForm):
    title = forms.CharField(
        label='Название',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    global_section = forms.ModelChoiceField(
        label='Направление бизнеса',
        required=True,
        queryset=Direction_of_business.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    section = forms.ModelChoiceField(
        label='Направление',
        required=False,
        queryset=Direction.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    category = forms.ModelChoiceField(
        label='Рубрика',
        required=True,
        queryset=Section.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    subcategory = forms.ModelChoiceField(
        label='Тип документа',
        required=True,
        queryset=Doc_class.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    file = forms.FileField(
        label='Файл версии (PDF)',
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf'
        })
    )
    
    file_type = forms.ChoiceField(
        label='Тип файла',
        choices=[('pdf', 'PDF')],
        initial='pdf',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    version_date = forms.DateField(
        label='Дата редакции',
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    comment = forms.CharField(
        label='Комментарий к версии',
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Краткое описание изменений'
        })
    )
    
    word_file = forms.FileField(
        label='Исходный Word-файл',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.docx,.doc'
        })
    )
    
    class Meta:
        model = DocumentVersion
        fields = ['title', 'global_section', 'section', 'category', 'subcategory', 'file', 'file_type', 'version_date', 'comment', 'word_file']


class SlideZipUploadForm(forms.Form):
    zip_file = forms.FileField(label='Архив с PNG-слайдами', required=True)

    def save(self, document):
        # Удаляем старые слайды перед загрузкой новых
        document.slides.all().delete()
        zip_file = self.cleaned_data['zip_file']
        with zipfile.ZipFile(zip_file) as archive:
            def natural_key(s):
                return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]
            slide_files = sorted(
                [f for f in archive.namelist() if f.lower().endswith('.png')],
                key=natural_key
            )
            for idx, name in enumerate(slide_files):
                data = archive.read(name)
                slide = PresentationSlide(
                    document=document,
                    order=idx
                )
                slide.image.save(name, ContentFile(data), save=True)


class DocumentPDFUpdateForm(DocumentForm):
    """Форма для обновления PDF-документа без файловых полей"""
    class Meta:
        model = Document
        fields = ['title', 'global_section', 'section', 'category', 'subcategory']


# --- Update form for mixed content (optional attachments) ---

class DocumentFileUpdateForm(DocumentFileForm):
    """Используется при редактировании mixed_content: можно добавить новые вложения, описание не обязателен."""
    
    class Meta(DocumentFileForm.Meta):
        fields = ['title', 'global_section', 'section', 'category', 'subcategory', 'description']