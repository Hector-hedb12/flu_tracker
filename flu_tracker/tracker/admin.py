from django.contrib.gis import admin
from django.utils.safestring import mark_safe

from .models import Tweet, AddressLocator


@admin.register(Tweet)
class TweetAdmin(admin.OSMGeoAdmin):
    list_display = ('ref', 'created', 'view_on_twitter')
    actions = None

    readonly_fields = ('ref',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def view_on_twitter(self, obj):
        url = 'https://twitter.com/i/status/{}'.format(obj.ref)
        return mark_safe(
            '<a href="{}" target="_blank">View on Twitter</a>'.format(url)
        )
    view_on_twitter.allow_tags = True
    view_on_twitter.short_description = 'View on Twitter'


@admin.register(AddressLocator)
class AddressLocatorAdmin(admin.OSMGeoAdmin):
    list_display = ('address', 'location',)
