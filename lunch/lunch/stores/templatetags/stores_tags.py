from django.template import Library

register = Library()


@register.filter
def deletable(store, user):
    return store.can_user_delete(user)
