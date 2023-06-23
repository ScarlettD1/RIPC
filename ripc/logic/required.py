from django.contrib.auth.decorators import user_passes_test

from ripc.logic.check_who_auth import some_rep_authenticated, region_rep_authenticated, org_rep_authenticated


# Функция проверки административных прав
def some_resp_required(login_url=None):
    return user_passes_test(some_rep_authenticated, login_url=login_url)


# Функция проверки прав представителя региона
def region_resp_required(login_url=None):
    return user_passes_test(region_rep_authenticated, login_url=login_url)


# Функция проверки прав представителя организации
def org_resp_required(login_url=None):
    return user_passes_test(org_rep_authenticated, login_url=login_url)
