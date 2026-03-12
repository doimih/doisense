import json

from django.core.management.base import BaseCommand

from core.models import NotificationDelivery
from payments.models import Payment
from users.models import User


TRIAL_NOTIFICATION_TYPES = {"trial_expiration_warning"}
UPSELL_NOTIFICATION_TYPES = {"upgrade_recommendation"}


class Command(BaseCommand):
    help = (
        "Audit manual VIP users and detect conflicts with trial, discounts, "
        "subscriptions, and notification rules."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--json",
            action="store_true",
            help="Print the audit report as JSON.",
        )
        parser.add_argument(
            "--fix-discount-flags",
            action="store_true",
            help="Normalize stored early_discount_eligible values to match current business rules.",
        )

    def handle(self, *args, **options):
        if options["fix_discount_flags"]:
            self._normalize_discount_flags()

        report = self._build_report()
        if options["json"]:
            self.stdout.write(json.dumps(report, ensure_ascii=True, default=str, indent=2))
            return

        self._write_human_report(report)

    def _normalize_discount_flags(self):
        updated = 0
        for user in User.objects.all().only("id", "vip_manual_override", "early_discount_eligible"):
            expected = user.expected_early_discount_eligibility()
            if user.early_discount_eligible != expected:
                User.objects.filter(pk=user.pk).update(early_discount_eligible=expected)
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Normalized early discount flags for {updated} user(s)."))

    def _build_report(self):
        manual_users = list(User.objects.filter(vip_manual_override=True).order_by("id"))
        validated_users = []
        detected_problems = []
        detected_conflicts = []
        wrongly_marked_users = []

        for user in manual_users:
            payment = Payment.objects.filter(user=user).order_by("-updated_at").first()
            user_problems = []
            user_conflicts = []

            if user.effective_plan_tier() != User.PLAN_VIP:
                user_problems.append("effective_tier_not_vip")

            if user.is_in_trial():
                user_conflicts.append("trial_logic_still_active")

            if user.early_discount_eligible:
                user_conflicts.append("early_discount_flag_active")

            if NotificationDelivery.objects.filter(
                user=user,
                notification_type__in=TRIAL_NOTIFICATION_TYPES,
            ).exists():
                user_conflicts.append("trial_notifications_sent")

            if NotificationDelivery.objects.filter(
                user=user,
                notification_type__in=UPSELL_NOTIFICATION_TYPES,
            ).exists():
                user_conflicts.append("upsell_notifications_sent")

            if payment and payment.plan_tier == "premium_discounted":
                user_conflicts.append("discounted_subscription_attached")

            if payment and payment.cancel_at_period_end:
                user_conflicts.append("subscription_cancel_state_present")

            if payment and payment.status == "past_due":
                user_conflicts.append("subscription_past_due_state_present")

            if not user.is_active or user.email.startswith("deleted.user."):
                wrongly_marked_users.append(
                    {
                        "id": user.id,
                        "email": user.email,
                        "reason": "inactive_or_deleted_account",
                    }
                )

            validated_users.append(
                {
                    "id": user.id,
                    "email": user.email,
                    "effective_tier": user.effective_plan_tier(),
                    "manual_vip": user.manual_vip,
                    "has_paid_access": user.has_paid_access(),
                    "trial_notifications_blocked": "trial_notifications_sent" not in user_conflicts,
                    "upsell_notifications_blocked": "upsell_notifications_sent" not in user_conflicts,
                    "subscription_logic_bypassed": user.effective_plan_tier() == User.PLAN_VIP,
                    "discount_logic_bypassed": not user.early_discount_eligible,
                    "payment_status": getattr(payment, "status", None),
                    "payment_plan_tier": getattr(payment, "plan_tier", None),
                }
            )

            for problem in user_problems:
                detected_problems.append({"user_id": user.id, "email": user.email, "problem": problem})
            for conflict in user_conflicts:
                detected_conflicts.append({"user_id": user.id, "email": user.email, "conflict": conflict})

        possible_missing_manual_vip = []
        vip_candidates = User.objects.filter(
            vip_manual_override=False,
            is_staff=False,
            is_superuser=False,
            plan_tier=User.PLAN_VIP,
        ).order_by("id")
        for user in vip_candidates:
            payment = Payment.objects.filter(user=user).order_by("-updated_at").first()
            active_vip_subscription = bool(payment and payment.status == "active" and payment.plan_tier == User.PLAN_VIP)
            if not active_vip_subscription:
                possible_missing_manual_vip.append(
                    {
                        "id": user.id,
                        "email": user.email,
                        "reason": "vip_tier_without_active_vip_subscription",
                        "payment_status": getattr(payment, "status", None),
                        "payment_plan_tier": getattr(payment, "plan_tier", None),
                    }
                )

        return {
            "manual_vip_count": len(validated_users),
            "validated_manual_vip_users": validated_users,
            "detected_problems": detected_problems,
            "wrongly_marked_users": wrongly_marked_users,
            "detected_conflicts": detected_conflicts,
            "possible_missing_manual_vip_users": possible_missing_manual_vip,
        }

    def _write_human_report(self, report):
        self.stdout.write(self.style.SUCCESS(f"Manual VIP users audited: {report['manual_vip_count']}"))

        self.stdout.write("Validated manual VIP users:")
        if report["validated_manual_vip_users"]:
            for item in report["validated_manual_vip_users"]:
                self.stdout.write(
                    f"- {item['id']} {item['email']} tier={item['effective_tier']} payment={item['payment_status'] or 'none'}"
                )
        else:
            self.stdout.write("- none")

        self.stdout.write("Detected problems:")
        if report["detected_problems"]:
            for item in report["detected_problems"]:
                self.stdout.write(f"- {item['email']}: {item['problem']}")
        else:
            self.stdout.write("- none")

        self.stdout.write("Detected conflicts:")
        if report["detected_conflicts"]:
            for item in report["detected_conflicts"]:
                self.stdout.write(f"- {item['email']}: {item['conflict']}")
        else:
            self.stdout.write("- none")

        self.stdout.write("Wrongly marked users:")
        if report["wrongly_marked_users"]:
            for item in report["wrongly_marked_users"]:
                self.stdout.write(f"- {item['email']}: {item['reason']}")
        else:
            self.stdout.write("- none")

        self.stdout.write("Possible missing manual VIP users:")
        if report["possible_missing_manual_vip_users"]:
            for item in report["possible_missing_manual_vip_users"]:
                self.stdout.write(f"- {item['email']}: {item['reason']}")
        else:
            self.stdout.write("- none")