# Django Published

Published allows for "Set it and forget it!" behavior for your models.

1.  You have a model where some number of instances of the model should
    be "live". A good example of this would be an Article model, where
    you've written some articles that are "live", some that might've
    been taken down, some that are still "in progress", and others that
    are ready to "go live", but have a "go live" date that's in the
    future.

Other features:

1.  If you're logged into the Django Admin, you can still "see" pages
    that aren't live (so you can easily QA things that are in progress).

## Quick start

1.  Add "published" to your INSTALLED_APPS setting like this:
```python
INSTALLED_APPS = [
    ...
    'published',
]
```


## Gatekeeping Models

The main use for django-published is where you have a model with many
instances, but you only want some to be "live" on the site.

A good example is a generic "Article" model:

>   - Some articles are ready-to-go and you want them live to the
>     public;
>   - Other articles are still being worked on - you want to be able to
>     preview them, but not take them live JUST yet;
>   - Some articles might be pulled (and re-published later)
>   - Some articles are ready to be published, but you want them to only
>     go live at a later date.

Here, all you need to do is subclass the
`PublishedAbstractModel` abstract class,
e.g.:

```python
from published.models import PublishedAbstractModel

class Article(PublishedAbstractModel):
    ...
```

The superclass creates two fields:

1.  `live_as_of` - this is the timestamp of when the object should go live. If
    it's not set (None) you can think of this as an "in development"
    phase. For an Article model, you've created the instance, but you're
    still writing the Article. You can preview it through the Admin, but
    it's not live on the site.

2.  `publish_status` - this has 3 possible values:
       - 0 = "use live_as_of" date to determine if the object is
         available to the public
       - 1 = "always on" - hard-wired to be always available to the
         public
       - -1 = "permanently off" - hard-wired to NEVER be available to
         the public

You set the `publish_status` and `live_as_of` values through the Admin.

### Generic Model Views

Setting up django-published for generic models views is easy! Using the 
Article model as an example, here is the corresponding view code for  
listing and detail views.

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

1.  In the ListView, django-published is filtering the model with the
    following rules:

     1.  If the user is logged in as staff, always include the model instance
     2.  If there is no user, and the
         `publish_status</span> = 1`, include
         the model instance.
     3.  If there is no user,
         <span class="title-ref">publish\_status</span> = 0, *and* the
         current date/time \>
         <span class="title-ref">live\_as\_of</span>, \_include the
    >     model [instance]().
     4.  Return the filtered list of model instances.

2.  In the DetailView, the gatekeeper follows the same rules, but will
    throw a 404 error, if the user is not logged in as staff and the
    request object isn't "live" yet.

### Custom Code

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

The `is_auth` parameter allows you to
filter based on whether the user making the request is logged in or not.
If they are logged in, then objects that aren't live but still available
to the Admin will "pass" through the gatekeeper. For this, you'd set
`is_auth = self.request.user.is_authenticated`.

I've found that I almost NEVER need that. Typically for constructed
lists of object you want to only see what IS live, so in almost every
case where I've used `view_gatekeeper`, I've set `is_auth = False`. 
You can still "see" all the non-live objects through their detail page when you're
logged into the Admin.

# The Admin Interface

Gatekeeper has several helper functions to customize the admin (it
doesn't have the admin methods because there's no way to know if there
are other ModelAdmins being used, and Python's MRO doesn't allow for
chaining). All of them are in the `gatekeeper.admin_helpers` file.

## Readonly Fields

To use any of the below functions, one field needs to be added to the admin instance.
This can be done using `add_to_readonly_fields`


1.  A `show_publish_status` that takes the `live_as_of` and `publish_status`
 fields and creates a human-friendly string from them

Example code:

```python
from published.admin_helpers import add_to_readonly_fields
from published.admin import PublishedAdmin

class MyModelAdmin(PublishedAdmin):
    readonly_fields = ['my_field_1', 'my_field_2'] + add_to_readonly_fields()
 ```

## List Display

To show the status in an admin list view, `show_publish_status` needs to be added to 
`list_display`

This can be added automatically with the `add_to_list_display` method, e.g.:

```python
from published.admin_helpers import add_to_list_display
from published.admin import PublishedAdmin

class MyModelAdmin(PublishedAdmin):
    list_display = ['pk', 'title', ] + add_to_list_display()
```

## Fieldsets

There are two ways to include the gatekeeper fields using the
`gatekeeper_add_to_fieldsets` method:

### As a separate section

There's a `section` attribute (default:
True) that returns the entire section tuple with the gatekeeper fields.
There's also a `collapse` attribute
(default: False) that uses the Django Admin "collapse" class.


```python
from published.admin_helpers import add_to_fieldsets
from published.admin import PublishedAdmin

class MyModelAdmin(PublishedAdmin):
    fieldsets = (
        (None, ...),
        add_to_fieldsets(section=True, collapse=False)
    )
```

### Included as part of a section

Or you can include them as part of another section; in this case you'd
set `section=False`

```python
from published.admin_helpers import add_to_fieldsets
from published.admin import PublishedAdmin

class MyModelAdmin(PublishedAdmin):
    fieldsets = (
        (None, {
            'fields': (
                (some set of fields),
                add_to_fieldsets(section=False)
            )
        }),
```

And of course you can just do it all manually with the editable `live_as_of`, `publish_status` fields and the readonly
`show_publish_status` field.