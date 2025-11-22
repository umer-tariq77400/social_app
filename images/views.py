from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ImageCreateForm
from .models import Image
from actions.utils import create_action


@login_required
def image_create(request):
    """
    Handle image creation. Accepts POST requests with image data and GET requests
    with image URL parameters for bookmarklet submission. Saves the image associated
    with the logged-in user and redirects to the image detail page on success.
    """
    if request.method == "POST":
        form = ImageCreateForm(request.POST)
        if form.is_valid():
            new_image = form.save(commit=False)

            new_image.user = request.user
            new_image.save()
            create_action(request.user, "bookmarked image", new_image)

            messages.success(request, "Image added successfully")

            return redirect(new_image.get_absolute_url())
    else:
        form = ImageCreateForm(data=request.GET)

    return render(
        request, "images/image/create.html", {"section": "images", "form": form}
    )


@login_required
def image_list(request):
    """
    Display a paginated list of all images. Supports AJAX requests that return
    only the image grid partial via the 'images_only' GET parameter. Displays
    8 images per page.
    """
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get("page")
    images_only = request.GET.get("images_only")
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            return HttpResponse("")
        images = paginator.page(paginator.num_pages)
    if images_only:
        return render(
            request,
            "images/image/list_images.html",
            {"section": "images", "images": images},
        )
    return render(
        request,
        "images/image/list.html",
        {"section": "images", "images": images},
    )


@login_required
def image_detail(request, id, slug):
    """
    Display detailed view of a specific image. Retrieved by both id and slug
    for SEO-friendly URLs. Returns 404 if image is not found.
    """
    image = get_object_or_404(Image, id=id, slug=slug)
    return render(
        request,
        "images/image/detail.html",
        {"section": "images", "image": image},
    )


@login_required
@require_POST
def image_like(request):
    """
    Handle image liking/unliking via AJAX POST requests. Accepts 'id' and 'action'
    parameters where action is either 'like' (add to user's likes) or any other value
    (remove from user's likes). Returns JSON response with status.
    """
    image_id = request.POST.get("id")
    action = request.POST.get("action")
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == "like":
                image.users_like.add(request.user)
                create_action(request.user, "likes", image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({"status": "ok"})
        except Image.DoesNotExist:
            pass
    return JsonResponse({"status": "error"})
