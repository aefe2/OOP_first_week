from django.db import models
import uuid  # Required for unique book instances
from datetime import date
from django.contrib.auth.models import User  # Required to assign User as a borrower
from django.urls import reverse  # To generate URLS by reversing URL patterns
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import forms
from django.utils.datetime_safe import datetime


class User(AbstractUser):
    class Meta(AbstractUser.Meta):
        pass


class Cover(models.Model):
    def validate_image(value):
        size_limit = 2 * 1024 * 1024
        if value.size > size_limit:
            raise forms.ValidationError('Файл слишком большой. Размер файла не должен превышать 2MB')

    cover = models.ImageField(validators=[validate_image], upload_to='cover/books/title', verbose_name='Изображения',
                              blank=True, null=False)

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'


class Language(models.Model):
    """Model representing a Language (e.g. English, French, Japanese, etc.)"""
    name = models.CharField(max_length=200,
                            help_text="Enter the book's natural language (e.g. English, French, Japanese etc.)")

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name


class Book(models.Model):
    objects = None
    """Model representing a book (but not a specific copy of a book)."""
    title = models.CharField(max_length=100, verbose_name='Название книги', blank=False, unique=False)
    author = models.ForeignKey('Author', on_delete=models.CASCADE, max_length=100, verbose_name='Автор', blank=False)
    yearOfRel = models.IntegerField(verbose_name='Год выпуска', blank=False,
                                    validators=[MinValueValidator(1000), MaxValueValidator(9999)])
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the book")
    isbn = models.CharField('ISBN', max_length=13,
                            unique=True,
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn'
                                      '">ISBN number</a>')
    genre = models.CharField(max_length=100, verbose_name='Жанр', blank=True)
    category = models.CharField(max_length=100, verbose_name='Категория', blank=True)
    publisher = models.CharField(max_length=100, verbose_name='Издательство', blank=True)
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    def validate_image(value):
        size_limit = 2 * 1024 * 1024
        if value.size > size_limit:
            raise forms.ValidationError('Файл слишком большой. Размер файла не должен превышать 2MB')

    photoPreview = models.ImageField(validators=[validate_image], upload_to='cover', verbose_name='Изображения',
                                     blank=False, null=True)
    bookFile = models.FileField(upload_to=' ', verbose_name='Файл с книгой', blank=False, null=True)

    class Meta:
        ordering = ['title', 'author']
        unique_together = ('title', 'author', 'yearOfRel', 'publisher')
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'

    # def display_genre(self):
    #     """Creates a string for the Genre. This is required to display genre in Admin."""
    #     return ', '.join([genre.name for genre in self.genre.all()[:3]])

    # display_genre.short_description = 'Genre'

    def get_absolute_url(self):
        """Returns the url to access a particular book instance."""
        return reverse('book-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return self.title


class BookInstance(models.Model):
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular book across whole library")
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_overdue(self):
        """Determines if the book is overdue based on due date and current date."""
        return bool(self.due_back and date.today() > self.due_back)

    LOAN_STATUS = (
        ('d', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='d',
        help_text='Book availability')

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        """String for representing the Model object."""
        return '{0} ({1})'.format(self.id, self.book.title)


class Author(models.Model):
    objects = None
    """Model representing an author."""
    name = models.CharField(max_length=100, verbose_name='Имя', blank=False)
    last_name = models.CharField(max_length=100, verbose_name='Отчество', blank=True)
    middle_name = models.CharField(max_length=100, verbose_name='Фамилия', blank=False)
    date_of_birth = models.DateField(max_length=100, verbose_name='Дата рождения', null=True, blank=True)
    date_of_death = models.DateField('died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'name']
        unique_together = ('name', 'last_name', 'middle_name', 'date_of_birth', 'date_of_death')
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return '{} {} {}'.format(self.name, self.last_name, self.middle_name, )
