import base64
import mimetypes
import requests
from django import forms
from django.core.files.base import ContentFile
from django.utils.text import slugify

from .models import Image


class ImageCreateForm(forms.ModelForm):
    file = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control"}),
    )
    edited_image = forms.CharField(widget=forms.HiddenInput(), required=False)
    mime_type = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Image
        fields = ["title", "url", "description", "prompt"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter image title"}
            ),
            "url": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter image URL"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter image description",
                    "rows": 4,
                }
            ),
            "prompt": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter a prompt to edit the image with AI",
                    "rows": 2,
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        url = cleaned_data.get("url")
        file = cleaned_data.get("file")

        if not url and not file:
            raise forms.ValidationError("Please provide either an image URL or upload a file.")
        
        if url and not file:
            # Only validate URL extension if we are downloading from URL
            valid_extensions = ["jpg", "jpeg", "png"]
            extension = url.rsplit(".", 1)[-1].lower()
            if extension not in valid_extensions:
                raise forms.ValidationError(
                    "The given URL does not match valid image extensions (jpg, jpeg, png)."
                )
        
        return cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):
        image = super().save(commit=False)
        image_url = self.cleaned_data.get("url")
        image_file = self.cleaned_data.get("file")
        
        name = slugify(image.title)

        if image_file:
            # If file is uploaded, save it directly
            image.original_image = image_file
        elif image_url:
            # If URL is provided, download it
            extension = image_url.rsplit(".", 1)[-1].lower()
            image_name = f"{name}.{extension}"
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                response = requests.get(image_url, headers=headers, timeout=10)
                if response.status_code != 200:
                    raise forms.ValidationError(
                        f"Unable to download image. Server returned status {response.status_code}."
                    )
                image.original_image.save(image_name, ContentFile(response.content), save=False)
            except requests.exceptions.Timeout:
                raise forms.ValidationError(
                    "Image download timed out. URL may be slow or invalid."
                )
            except requests.exceptions.RequestException as e:
                raise forms.ValidationError(f"Error downloading image: {str(e)}")

        edited_image_data = self.cleaned_data.get("edited_image")
        if edited_image_data:
            image_data = base64.b64decode(edited_image_data)
            mime_type = self.cleaned_data.get("mime_type")
            extension = mimetypes.guess_extension(mime_type)
            image.edited_image.save(
                f"{slugify(name)}_edited{extension}",
                ContentFile(image_data),
                save=False,
            )

        if commit:
            image.save()
        return image
