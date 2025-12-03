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

    class Meta:
        model = Image
        fields = ["title", "url", "description"]
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
        }

    def clean(self):
        cleaned_data = super().clean()
        url = cleaned_data.get("url")
        file = cleaned_data.get("file")

        if not url and not file:
            raise forms.ValidationError("Please provide either an image URL or upload a file.")
        
        return cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):
        image = super().save(commit=False)
        image_url = self.cleaned_data.get("url")
        image_file = self.cleaned_data.get("file")
        
        name = slugify(image.title)

        if image_file:
            # If file is uploaded, save it directly
            image.image = image_file
        elif image_url:
            # If URL is provided, download it
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                response = requests.get(image_url, headers=headers, timeout=10)
                if response.status_code != 200:
                    raise forms.ValidationError(
                        f"Unable to download image. Server returned status {response.status_code}."
                    )
                
                # Determine extension from content-type or URL
                content_type = response.headers.get("Content-Type", "")
                extension = "jpg" # Default
                if "image/jpeg" in content_type:
                    extension = "jpg"
                elif "image/png" in content_type:
                    extension = "png"
                elif "." in image_url.split("/")[-1]:
                     # Fallback to URL extension if available
                     ext = image_url.rsplit(".", 1)[-1].lower()
                     if ext in ["jpg", "jpeg", "png"]:
                         extension = ext

                image_name = f"{name}.{extension}"
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
