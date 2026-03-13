from botocore.config import Config
import boto3

from django.core.management.base import BaseCommand

from core.models import BackupVerificationLog
from core.system_config import get_system_config


class Command(BaseCommand):
    help = "Verify backup bucket connectivity and presence of backup objects, then write a BackupVerificationLog entry."

    def handle(self, *args, **options):
        config = get_system_config()

        if not config.backup_enabled:
            notes = "Backup verification skipped because backup storage is disabled."
            BackupVerificationLog.objects.create(
                status=BackupVerificationLog.STATUS_FAILED,
                source="platform_scheduler",
                notes=notes,
            )
            self.stderr.write(notes)
            return

        missing_fields = []
        if not config.backup_s3_endpoint:
            missing_fields.append("endpoint")
        if not config.backup_s3_bucket:
            missing_fields.append("bucket")
        if not config.backup_access_key_id:
            missing_fields.append("access key")
        if not config.backup_secret_access_key:
            missing_fields.append("secret key")

        if missing_fields:
            notes = f"Backup verification failed: missing {', '.join(missing_fields)}."
            BackupVerificationLog.objects.create(
                status=BackupVerificationLog.STATUS_FAILED,
                source="platform_scheduler",
                notes=notes,
            )
            self.stderr.write(notes)
            return

        prefix = (config.backup_s3_path_prefix or "").strip().strip("/")

        try:
            client = boto3.client(
                "s3",
                endpoint_url=(config.backup_s3_endpoint or "").strip(),
                aws_access_key_id=config.backup_access_key_id,
                aws_secret_access_key=config.backup_secret_access_key,
                region_name=config.backup_region or None,
                config=Config(
                    s3={
                        "addressing_style": "path" if config.backup_force_path_style else "auto"
                    }
                ),
            )
            client.head_bucket(Bucket=config.backup_s3_bucket)
            response = client.list_objects_v2(
                Bucket=config.backup_s3_bucket,
                Prefix=f"{prefix}/" if prefix else "",
                MaxKeys=20,
            )
            contents = response.get("Contents", [])
            if not contents:
                notes = (
                    f"Backup bucket reachable, but no objects found under prefix '{prefix or '/'}'."
                )
                status = BackupVerificationLog.STATUS_FAILED
                self.stderr.write(notes)
            else:
                sample_keys = ", ".join(item.get("Key", "") for item in contents[:3])
                notes = (
                    f"Backup verification passed. Found {len(contents)} object(s) under "
                    f"prefix '{prefix or '/'}'. Sample: {sample_keys}"
                )
                status = BackupVerificationLog.STATUS_SUCCESS
                self.stdout.write(self.style.SUCCESS(notes))

            BackupVerificationLog.objects.create(
                status=status,
                source="platform_scheduler",
                notes=notes,
            )
        except Exception as exc:
            notes = f"Backup verification failed: {exc}"
            BackupVerificationLog.objects.create(
                status=BackupVerificationLog.STATUS_FAILED,
                source="platform_scheduler",
                notes=notes,
            )
            self.stderr.write(notes)