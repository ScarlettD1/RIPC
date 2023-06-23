from ripc.models import OrganizationRep, RegionRep


# Функция проверки пользователя, но причастность к одной из ролей представителей или администратора
def some_rep_authenticated(user):
    if user:
        if OrganizationRep.objects.filter(user=user.id).exists():
            return True
        if RegionRep.objects.filter(user=user.id).exists():
            return True
        if user.is_superuser:
            return True
    return False


# Функция проверки пользователя, на права представителя региона или администратора
def region_rep_authenticated(user):
    if user:
        if RegionRep.objects.filter(user=user.id).exists():
            return True
        if user.is_superuser:
            return True
    return False


# Функция проверки пользователя, на права представителя организации или администратора
def org_rep_authenticated(user):
    if user:
        if OrganizationRep.objects.filter(user=user.id).exists():
            return True
        if user.is_superuser:
            return True
    return False
