from ripc.models import OrganizationEvent


class Monitor:
    def check(self, org_event_id):
        event = OrganizationEvent.objects.get(pk=org_event_id)
        #bruh TODO: пиши код сука