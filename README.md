# Django Published [![PyPI](https://img.shields.io/pypi/v/django-published)](https://pypi.org/project/django-published/)

Published allows you to control the public visibility of model instances.
Useful in situations like below!

    You have a model where some number of instances of the model should
    be "live". A good example of this would be an Article model, where
    you've written some articles that are "live", some that might've
    been taken down, some that are still "in progress", and others that
    are ready to "go live", but have a "go live" date that's in the
    future.


This project is based on [django-model-gatekeeper](https://github.com/WGBH/django-model-gatekeeper) by
[WGBH](https://github.com/WGBH/).

# Getting Started

## Installation

1.  Add "published" to your `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    ...
    'published',
]
```

## Setting Up Models

The main use for *django-published* is where you have a model with many
instances, but you only want some to be "live" on the site.

A good example is a generic "Article" model:

>   - Some articles are ready-to-go and you want them live to the
>     public;
>   - Other articles are still being worked on - you want to be able to
>     preview them, but not take them live JUST yet;
>   - Some articles might be pulled (and re-published later)
>   - Some articles are ready to be published, but you want them to only
>     go live at a later date.

To start using this, all you need to do is subclass the
`PublishedModel` abstract model,
e.g:

```python
from published.models import PublishedModel

class Article(PublishedModel):
    ...
```

The superclass creates two fields:

1.  `publish_status` - this has 3 possible values:
       - **NEVER_AVAILABLE** = "permanently off" - hard-wired to NEVER be available to
         the public
       - **AVAILABLE_AFTER** = "use live_as_of" date to determine if the object is
         available to the public
       - **AVAILABLE** = "always on" - hard-wired to be always available to the
         public


2.  `live_as_of` - this is the timestamp of when the object should go live, if publish_status
    is **AVAILABLE_AFTER**



You set the `publish_status` and `live_as_of` values through the admin.

# The Frontend

## Generic Model Views

Setting up _django-published_ for generic models views is easy!

Using the Article model as an example, here is the corresponding
view code for  listing and detail views.

```python
from django.views.generic import DetailView, ListView
from .models import Article
from published.mixins import PublishedListMixin, PublishedDetailMixin

class ArticleListView(PublishedListMixin, ListView):
    model = Article
    template_name = 'article/article_list.html'
    context_object_name = 'articles'

class ArticleDetailView(PublishedDetailMixin, DetailView):
    model = Article
    template_name = 'article/article_detail.html'
    context_object_name = 'article'
```


What's happening behind the scenes:

1.  In the ListView, *django-published* is filtering the model with the
    following rules:

     1.  If the current user has admin access, always include the model instance.
     2.  If `publish_status = AVAILABLE`, include the model instance.
     3.  If `publish_status = NEVER_AVAILABLE`, DO NOT the model instance.
     4.  If `publish_status = AVAILABLE_AFTER`, *and* the current date/time is after
         `live_as_of`, include the model instance.
     4.  Return the filtered list of model instances.

2.  In the DetailView, *django-published* follows the same rules but will
    throw a 404 error if the model instance is not available.

## Custom Code

Say there's a section on your homepage that gives a list of the three
most recent articles. If you just create a queryset along the lines of:

    most_recent_articles = Article.objects.order_by(-date_created)[:3]

it will include articles regardless of what their gatekeeping situation
is.

So there is a helper function to apply the gatekeeping rules to any
queryset you generate.

#### queryset_filter
This takes a queryset, applies the rules and returns a filtered queryset.

```python
from published.utils import queryset_filter
...
recent_articles = Article.objects.order_by('-date_created')
recent_articles = queryset_filter(recent_articles, is_auth)
...
```


By default, `queryset_filter` does not apply the same exceptions as the view
mixins above. This means that unpublished model instances will be *not* displayed
if the current user has admin access.

The optional `user` parameter allows you to enable this special case, as seen below.
```python
queryset_filter(queryset, user=self.request.user)
```

#### available_to_public

**Note**: This should only be used in templates

If you need to check if an object is considered "available" in a Django template, you can use the
`available_to_public` model attribute, as below.

```djangotemplate
{% for article in article_list %}
    {% if article.available_to_public %}
        I'm published!
    {% endif %}
{% endfor %}
```

# The Admin Interface

*django-published* has several helper functions to make adding admin controls easier.
All of them can be found in the  `django-published.admin` module.

![alt test](https://raw.githubusercontent.com/dmptrluke/django-published/master/screenshots/admin.png)

## Setting Up
All of the below functions require the use of the `PublishedAdmin` abstract class instead
of the default `ModelAdmin` class. You can see examples of this in all of the code below.

Additionally, `add_to_readonly_fields` also needs to be added to `readonly_fields` to provide some of 
the fields needed later on.

```python
from published.admin import PublishedAdmin

class ArticleAdmin(PublishedAdmin):
    readonly_fields = ['my_field_1', 'my_field_2'] + add_to_readonly_fields()
    ...
```

## Adding to List View

To show the status in an admin list view, `show_publish_status` needs to be added to
`list_display`

This can be added automatically with the `add_to_list_display` method, e.g.:

```python
from published.admin import PublishedAdmin, add_to_list_display

class ArticleAdmin(PublishedAdmin):
    list_display = ['pk', 'title', ] + add_to_list_display()
```

## Adding to Edit View

To add the admin controls to your model, use `add_to_fieldsets`. The `collapse` attribute can be used 
to make the controls hidden by default.

```python
from published.admin import PublishedAdmin, add_to_fieldsets

class MyModelAdmin(PublishedAdmin):
    fieldsets = (
        (None, ...),
        add_to_fieldsets(section=True, collapse=False)
    )
```

If you don't want to use `add-to_fieldsets`, you can also add the fields manually, with the editable `live_as_of`, `publish_status` fields and the readonly
`show_publish_status` field.

## License

This software is released under the MIT license.
```
Copyright (c) 2019 WGBH Educational Foundation
Copyright (c) 2019-2023 Luke Rogers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
```
