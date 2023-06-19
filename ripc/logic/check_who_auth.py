from ripc.models import OrganizationRep, RegionRep


def some_rep_authenticated(user):
    if user:
        if OrganizationRep.objects.filter(user=user.id).exists():
            return True
        if RegionRep.objects.filter(user=user.id).exists():
            return True
        if user.is_superuser:
            return True
    return False


def region_rep_authenticated(user):
    if user:
        if RegionRep.objects.filter(user=user.id).exists():
            return True
        if user.is_superuser:
            return True
    return False


def org_rep_authenticated(user):
    if user:
        if OrganizationRep.objects.filter(user=user.id).exists():
            return True
        if user.is_superuser:
            return True
    return False
