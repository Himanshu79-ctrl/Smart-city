from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from reports.models import IssueReport
from .models import CitizenRewardProfile, PointsTransaction


@receiver(post_save, sender=IssueReport)
def issue_reported(sender, instance, created, **kwargs):

    if created:
        profile, created_profile = CitizenRewardProfile.objects.get_or_create(user=instance.citizen)

        profile.total_points += 10
        profile.issues_reported += 1
        profile.update_level()
        profile.save()

        PointsTransaction.objects.create(
            user=instance.citizen,
            transaction_type='issue_reported',
            points=10,
            description=f"Issue reported: {instance.title}",
            related_issue=instance
        )


@receiver(post_delete, sender=IssueReport)
def issue_deleted(sender, instance, **kwargs):

    try:
        profile = CitizenRewardProfile.objects.get(user=instance.citizen)

        profile.total_points -= 10
        profile.issues_reported -= 1
        profile.update_level()
        profile.save()

        PointsTransaction.objects.create(
            user=instance.citizen,
            transaction_type='bonus',
            points=-10,
            description=f"Issue deleted: {instance.title}",
        )

    except CitizenRewardProfile.DoesNotExist:
        pass