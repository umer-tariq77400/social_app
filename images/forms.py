import requests
from django import forms
from django.core.files.base import ContentFile
from django.utils.text import slugify

from .models import Image


class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ["title", "description", "url"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter image title"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter image description",
                    "rows": 4,
                }
            ),
            "url": forms.HiddenInput,
        }

    def clean_url(self):
        url = self.cleaned_data.get("url")
        valid_extensions = ["jpg", "jpeg", "png"]
        extension = url.rsplit(".", 1)[-1].lower()
        if extension not in valid_extensions:
            raise forms.ValidationError(
                "The given URL does not match valid image extensions (jpg, jpeg, png)."
            )
        return url

    def save(self, force_insert=False, force_update=False, commit=True):
        image = super().save(commit=False)
        image_url = self.cleaned_data.get("url")
        name = slugify(image.title)
        extension = image_url.rsplit(".", 1)[-1].lower()
        image_name = f"{name}.{extension}"
        # Download the image from the URL
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(image_url, headers=headers, timeout=10)
            if response.status_code != 200:
                raise forms.ValidationError(
                    f"Unable to download image. Server returned status {response.status_code}."
                )
            image.image.save(image_name, ContentFile(response.content), save=False)
        except requests.exceptions.Timeout:
            raise forms.ValidationError(
                "Image download timed out. URL may be slow or invalid."
            )
        except requests.exceptions.RequestException as e:
            raise forms.ValidationError(f"Error downloading image: {str(e)}")

        if commit:
            image.save()
        return image
