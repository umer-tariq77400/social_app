import redis
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from actions.utils import create_action

from .forms import ImageCreateForm
from .models import Image

r = redis.from_url(settings.REDIS_URL)

@login_required
def image_create(request):
    """
    Handle image creation via a form. On GET requests, display the form with
    pre-filled data from GET parameters. On POST requests, validate and save
    """
    if request.method == "POST":
        form = ImageCreateForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            new_image = form.save(commit=False)

            new_image.user = request.user
            new_image.save()
            create_action(request.user, "bookmarked image", new_image)

            messages.success(request, "Image added successfully")

            return redirect(new_image.get_absolute_url())
    else:
        # Use 'initial' instead of 'data' to pre-fill form without triggering validation
        form = ImageCreateForm(initial=request.GET)

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
    
    # Fetch view counts from Redis using pipeline for efficiency.
    try:
        pipeline = r.pipeline()
        for image in images:
            pipeline.get(f"image:{image.id}:views")
        view_counts = pipeline.execute()
        
        # Attach view counts to image objects
        for image, views in zip(images, view_counts):
            image.views = int(views) if views else 0
    except Exception:
        # If Redis is unavailable, set all view counts to 0
        for image in images:
            image.views = 0
    
    if images_only:
        return render(
            request,
            "includes/list_images_subset.html",
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

    # Safely increment view counters; if Redis is unavailable, fallback gracefully
    try:
        total_views = r.incr(f"image:{image.id}:views")
        r.zincrby("image_ranking", 1, image.id)
    except Exception:
        # Redis might not be configured or reachable; default to 0 views
        total_views = 0

    return render(
        request,
        "images/image/detail.html",
        {"section": "images", "image": image, "total_views": total_views},
    )


@login_required
def image_ranking(request):
    image_ranking = r.zrange("image_ranking", 0, -1, withscores=True, desc=True)[:10]
    image_ranking_ids = [int(id) for id, score in image_ranking]
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    
    # Fetch view counts from Redis using pipeline for efficiency
    try:
        pipeline = r.pipeline()
        for image in most_viewed:
            pipeline.get(f"image:{image.id}:views")
        view_counts = pipeline.execute()
        
        # Attach view counts to image objects
        for image, views in zip(most_viewed, view_counts):
            image.views = int(views) if views else 0
    except Exception:
        # If Redis is unavailable, set all view counts to 0
        for image in most_viewed:
            image.views = 0
    
    return render(
        request,
        "images/image/ranking.html",
        {"section": "images", "most_viewed": most_viewed},
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
