from django.contrib import admin
from django.conf import settings
from bot.models import User, Category, Content, Country, Link, User_category, User_content, SentLinks

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Content)
admin.site.register(Country)
admin.site.register(Link)

# Not available in release mode
if settings.DEBUG:
    admin.site.register(User_category)
    admin.site.register(User_content)
    admin.site.register(SentLinks)
