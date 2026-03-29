from django import forms

from .models import Prompt
from .validators import ENGLISH_ONLY_ERROR, validate_english_prompt_content


class PromptAdminForm(forms.ModelForm):
    class Meta:
        model = Prompt
        fields = "__all__"
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 25,
                    "style": "width: 100%; font-family: monospace;",
                    "spellcheck": "false",
                }
            )
        }
        help_texts = {
            "content": "All prompt content must be written in English.",
        }

    def clean_content(self):
        content = self.cleaned_data.get("content", "")
        validate_english_prompt_content(content)
        return content

    def clean_language(self):
        language = (self.cleaned_data.get("language") or "en").strip().lower()
        if language != "en":
            raise forms.ValidationError(ENGLISH_ONLY_ERROR)
        return language
