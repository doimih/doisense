from django.template.loader import render_to_string


def render_basic_email_html(
    *,
    title: str,
    body_text: str,
    action_url: str | None = None,
    action_label: str | None = None,
) -> str:
    return render_to_string(
        "emails/basic_message.html",
        {
            "title": title,
            "body_text": body_text,
            "action_url": action_url,
            "action_label": action_label or "Open",
        },
    )
