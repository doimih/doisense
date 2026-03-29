from difflib import HtmlDiff, unified_diff

from django.db.models import Max

from .models import Prompt, PromptVersion


def create_prompt_version(
    *,
    prompt: Prompt,
    updated_by: str = "",
    change_reason: str = "",
) -> PromptVersion:
    last_version = prompt.versions.aggregate(max_version=Max("version_number"))["max_version"] or 0
    return PromptVersion.objects.create(
        prompt=prompt,
        version_number=last_version + 1,
        content_snapshot=prompt.content,
        type_snapshot=prompt.type,
        language_snapshot=prompt.language,
        updated_by=updated_by,
        change_reason=change_reason,
    )


def list_prompt_versions(prompt: Prompt):
    return prompt.versions.order_by("-version_number", "-updated_at")


def rollback_prompt_to_version(
    prompt: Prompt,
    version: PromptVersion,
    *,
    updated_by: str = "",
    change_reason: str = "",
) -> Prompt:
    if version.prompt_id != prompt.pk:
        raise ValueError("The selected version does not belong to this prompt.")

    prompt.content = version.content_snapshot
    prompt.type = version.type_snapshot
    prompt.language = version.language_snapshot
    prompt._updated_by = updated_by
    prompt._change_reason = change_reason or f"Rollback to version {version.version_number}"
    prompt.save()
    return prompt


def compare_prompt_versions(version_a: PromptVersion, version_b: PromptVersion) -> dict:
    left = (version_a.content_snapshot or "").splitlines()
    right = (version_b.content_snapshot or "").splitlines()
    return {
        "from_version": version_a.version_number,
        "to_version": version_b.version_number,
        "unified_diff": "\n".join(
            unified_diff(
                left,
                right,
                fromfile=f"v{version_a.version_number}",
                tofile=f"v{version_b.version_number}",
                lineterm="",
            )
        ),
        "html_diff": HtmlDiff().make_table(
            left,
            right,
            f"v{version_a.version_number}",
            f"v{version_b.version_number}",
        ),
    }
