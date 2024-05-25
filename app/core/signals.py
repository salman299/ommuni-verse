from django.db.models.signals import post_save
from django.dispatch import receiver

from app.core.models import Person

@receiver(post_save, sender=Person)
def set_person_id(sender, instance, created, **kwargs):
    if created and not instance.person_id:
        # Get the maximum existing person_id, extract the number and increment it
        last_person = Person.objects.order_by('person_id').last()
        if last_person and last_person.person_id.isdigit():
            last_person_id = int(last_person.person_id)
            new_person_id = f"{last_person_id + 1:08d}"
        else:
            new_person_id = "00000001"
        
        instance.person_id = new_person_id
        instance.save()
