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

The main use for gatekeeping is where you have a model with many
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
<span class="title-ref">PublishedAbstractModel</span> abstract class,
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

2.  `publish_status` - this has 4 possible values:
    
       - 0 = "use live\_as\_of" date to determine if the object is
         available to the public
       - 1 = "always on" - hard-wired to be always available to the
         public
       - \-1 = "permanently off" - hard-wired to NEVER be available to
         the public

You set the <span class="title-ref">publish\_status</span> and
<span class="title-ref">live\_as\_of</span> values through the Admin.

### View Code

Setting up gatekeeping for models is easy\! Using the Article model as
an example, here is the corresponding view code for a listing and a
detail view.

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

1.  In the ListView, the gatekeeper is filtering the model with the
    following rules:
    
    > 1.  If the user is logged into the Admin and
    >     <span class="title-ref">publish\_status</span> \!= -1,
    >     \_include the model [instance]()
    > 2.  If there is no user, and the
    >     <span class="title-ref">publish\_status</span> = 1, \_include
    >     the model [instance]()
    > 3.  If there is no user,
    >     <span class="title-ref">publish\_status</span> = 0, *and* the
    >     current date/time \>
    >     <span class="title-ref">live\_as\_of</span>, \_include the
    >     model [instance]().
    > 4.  Return the filtered list of model instances.

2.  In the DetailView, the gatekeeper follows the same rules, but will
    throw a 404 error, if the user is not logged into the Admin and the
    request object isn't "live" yet.

\#\# Using the Gatekeeper with querysets in your own code

Say there's a section on your homepage that gives a list of the three
most recent articles. If you just create a queryset along the lines of:

    most_recent_articles = Article.objects.order_by(-date_created)[:3]

it will include articles regardless of what their gatekeeping situation
is.

So there are two helper functions to apply the gatekeeping rules to any
queryset you generate.

#### view_gatekeeper

This takes a queryset, applies the rules and returns a filtered
queryset.

```python
from published.view_utils import view_gatekeeper
...
recent_articles = Article.objects.order_by('-date_created')
recent_articles = view_gatekeeper(recent_articles, is_auth)
...
```

The `is_auth` parameter allows you to
filter based on whether the user making the request is logged in or not.
If they are logged in, then objects that aren't live but still available
to the Admin will "pass" through the gatekeeper. For this, you'd set
`is_auth =
self.request.user.is_authenticated`. (About the only time I can
see doing this is if you want to see how a particular non-live object
will "play" in a generated content feature.)

I've found that I almost NEVER need that. Typically for constructed
lists of object you want to only see what IS live, so in almost every
case where I've used `view_gatekeeper`,
I've set `is_auth = False`. You can still
"see" all the non-live objects through their detail page when you're
logged into the Admin.

#### object_gatekeeper

This takes a single object instance and returns True or False depending
on whether it "passes" the gate.

```python
from published.view_utils import object_gatekeeper
...
my_article = Article.objects.first()
am_i_avaiable = object_gatekeeper(my_article, is_auth)
...
```

Generally, you don't need this method since the model property
`available_to_public` already exists. The
one case where I've needed it was when I had a list come from an outside
source where there was an overlap with objects in one of my models. I
wanted to show all the external object, and construct links to the
object that overlapped but ONLY if they were live.

# The Admin Interface

Gatekeeper has several helper functions to customize the admin (it
doesn't have the admin methods because there's no way to know if there
are other ModelAdmins being used, and Python's MRO doesn't allow for
chaning). All of them are in the
`gatekeeper.admin_helpers` file.

## Readonly Fields

Example code:

```python
from published.admin_helpers import add_to_readonly_fields
from published.admin import PublishedAdmin

class MyModelAdmin(PublishedAdmin): 
    readonly_fields = ['my_field_1', 'my_field_2'] + add_to_readonly_fields()   
 ```

## List Display

For the basic gatekeeper, two fields are usually added to the
<span class="title-ref">list\_display</span> (they'll appear after
anything set in the ModelAdmin):

1.  A <span class="title-ref">show\_publish\_status</span> that takes
    the <span class="title-ref">live\_as\_of</span> and
    <span class="title-ref">publish\_status</span> fields and creates a
    human-friendly string from them;
2.  A <span class="title-ref">available\_to\_public</span> model
    property that returns True/False to show "is this available to the
    public"?


These can be added with the
<span class="title-ref">gatekeeper\_add\_to\_list\_display</span>
method, e.g.:

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