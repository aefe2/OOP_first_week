from django.contrib import admin
from .models import Author, Book, BookInstance, Language


# Define the admin class
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'name', 'middle_name', 'date_of_birth', 'date_of_death')
    fields = ['name', 'last_name', 'middle_name', ('date_of_birth', 'date_of_death')]


# Register the admin class with the associated model
admin.site.register(Author, AuthorAdmin)


# Register the Admin classes for Book using the decorator
class BooksInstanceInline(admin.TabularInline):
    list_display = ('title', 'status', 'due_back', 'id')
    model = BookInstance


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author')
    inlines = [BooksInstanceInline]


# Register the Admin classes for BookInstance using the decorator
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )


admin.site.register(Language)
