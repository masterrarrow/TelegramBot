from django.db import models
import datetime


class Category(models.Model):
    name = models.CharField(verbose_name='Название категории', max_length=30)

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return 'Category({name})'.format(name=self.name)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Content(models.Model):
    name = models.CharField(verbose_name='Название контента', max_length=30)

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return 'Content({name})'.format(name=self.name)

    class Meta:
        verbose_name = 'Контент'
        verbose_name_plural = 'Контент'


class Country(models.Model):
    name = models.CharField(verbose_name='Страна', max_length=30)

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return 'Country({name})'.format(name=self.name)

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'


class Link(models.Model):
    content = models.ForeignKey(
        Content, on_delete=models.CASCADE, verbose_name='Контент')
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name='Категория')
    name = models.CharField(verbose_name='Название',
                            max_length=200, default='')
    date = models.DateField(verbose_name='Дата добавления',
                            default=datetime.date.today)
    link = models.CharField(verbose_name='Ссылка', unique=True, max_length=200, default='')
    image_link = models.CharField(
        verbose_name='Ссылка на изображение', max_length=200, default='')
    description = models.CharField(
        verbose_name='Описание', max_length=200, default='')
    # clicks = models.PositiveIntegerField(verbose_name='Количество переходов', default=0)

    def __str__(self):
        return f'{self.content} / {self.category} / {self.name} / {self.link}'

    def __repr__(self):
        return 'Link({content}, {category}, {link})'.format(content=self.content,
                                                            category=self.category,
                                                            link=self.link)

    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'


class User(models.Model):
    user_id = models.CharField(verbose_name='Telegram ID', max_length=20)
    name = models.CharField(verbose_name='Имя пользователя', max_length=20)
    country = models.ForeignKey(
        Country, on_delete=None, blank=True, null=True, verbose_name='Страна')
    """
    category = models.ManyToManyField(
        Category, related_name='user_category', null=True, blank=True, required=False)
    content = models.ManyToManyField(
        Content, related_name='user_content', null=True, blank=True, required=False)
    """

    def __str__(self):
        return f'{self.user_id} / {self.name}'

    def __repr__(self):
        return 'User({id}, {name}, {country})'.format(id=self.user_id,
                                                      name=self.name, country=self.country)

    class Meta:
        # Name for admin page
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class User_category(models.Model):
    """
        Created to fix a problems in Django 2.2.3 with
        ManuToMany field: blank=True - doesn't work
    """
    user_id = models.ForeignKey(User, on_delete=models.CASCADE,
                                blank=True, null=True, verbose_name='Пользователь')
    user_category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                      blank=True, null=True, verbose_name='Категория')

    def __str__(self):
        return f'{self.user_id} / {self.user_category}'

    class Meta:
        # Name for admin page
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории пользователя'


class User_content(models.Model):
    """
        Created to fix a problems in Django 2.2.3 wit
        ManuToMany field: blank=True - doesn't work
    """
    user_id = models.ForeignKey(User, on_delete=models.CASCADE,
                                blank=True, null=True, verbose_name='Пользователь')
    user_content = models.ForeignKey(Content, on_delete=models.CASCADE,
                                     blank=True, null=True, verbose_name='Контент')

    def __str__(self):
        return f'{self.user_id} / {self.user_content}'

    class Meta:
        # Name for admin page
        verbose_name = 'Контент'
        verbose_name_plural = 'Контент пользователя'


class SentLinks(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             blank=True, null=True, verbose_name='Пользователь')
    link = models.ForeignKey(Link, on_delete=models.CASCADE,
                             blank=True, null=True, verbose_name='Канал')

    def __str__(self):
        return f'{self.user} / {self.link}'

    def __repr__(self):
        return 'SentLinks({user}, {link})'.format(user=self.user, link=self.link)

    class Meta:
        verbose_name = 'Рассылка каналов'
        verbose_name_plural = 'Рассылка каналов'
