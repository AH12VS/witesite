from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect
from django.utils.text import slugify
from django.db.models import Q, Count
from django.contrib.postgres.search import SearchQuery
from taggit.models import Tag
from .models import PostModel, CommentModel
from .forms import CommentForm, AddPostForm

_CLASSY_POEMS = [
    "آتیش گیزه قمه چیه وقتی کلمه هام خودش تیزه",
    "ماشینش سبزه چشمام قرمز جی بام اسلیم کندال جنر",
    "تو چشات معجزه میکرد حالا شدی موجب این درد",
    "پررو قرنیه مشکی قلدر چار شونه کشتی",
    "هر شب هر صبح هر روزو یکسره آژیر مامورو",
    "سینه نزن اینجا هیيت نی راس بگو قمه رو کجات غیب کردی",
    "به درندگیه کوسه ایم با مغز دلفین",
    "رد شدم رفتم از اونایی که پی جنجالن",
]


def posts_view(request, tag_slug=None):
    posts = PostModel.objects.filter(status="published")

    tag = None
    if tag_slug:
        tag = Tag.objects.get(slug=tag_slug)
        posts = posts.filter(tags__in=[tag])

    page_num = request.GET.get("page", 1)
    paginator = Paginator(posts, 15)
    # paginator = Paginator(posts, 1)

    try:
        posts = paginator.page(page_num)
    except EmptyPage:
        paginator.page(1)
    except PageNotAnInteger:
        paginator.page(paginator.num_pages)

    _classy_poems = _CLASSY_POEMS

    context = {
        "posts": posts,
        "page": page_num,
        "tag": tag,
        "classy_poems": _classy_poems,
    }

    return render(request, "posts/posts.html", context)


def postdetail_view(request, pk, slug):
    post = get_object_or_404(PostModel, slug=slug, pk=pk)
    comments = CommentModel.objects.filter(post=post, active="True")

    if request.user.is_authenticated:
        if request.user == post.author:
            return redirect("posts:postdetail_edit_page", slug=slug, pk=pk)

    new_commnet = None
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            new_commnet = CommentModel()
            cd = form.cleaned_data
            new_commnet.name = cd["name"]
            new_commnet.comment = cd["comment"]
            new_commnet.post = post
            new_commnet.save()
            return HttpResponseRedirect("")
    else:
        form = CommentForm()

    tag_ids = post.tags.values_list("id", flat=True)
    similar_posts = PostModel.objects.all().filter(
        status="published", tags__in=tag_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(
        s_count=Count("tags")).order_by("-s_count", "-publish")

    context = {
        "post": post,
        "comments": comments,
        "form": form,
        "new_comment": new_commnet,
        "similar_posts": similar_posts,
    }

    return render(request, "posts/postdetail.html", context)


def add_post_view(request):
    if not request.user.is_authenticated:
        return redirect("login:login_page")
    if request.method == "POST":
        form = AddPostForm(request.POST)
        if form.is_valid():
            post = PostModel()
            cd = form.cleaned_data
            post.title = cd["title"]
            post.body = cd["body"]
            post.author = request.user
            slug = str(post.author) + "-" + str(post.title) + \
                "-" + str(post.time_for_slg)
            post.slug = slugify(slug)
            post.save()
            post.tags.add(str(post.title))
            post.tags.add(str(post.author))
            post.tags.add(str(post.time_for_slg))

            return redirect("users:user_detail_page")
    else:
        form = AddPostForm()

    context = {
        "form": form,
    }

    return render(request, "posts/add-post.html", context)


def search_view(request, tag_slug=None):
    posts = PostModel.objects.filter(status="published")

    if request.method == "GET":

        search_val = str(request.GET.get("search-val"))

        if search_val:

            request.session["search_val_session"] = search_val
        else:
            try:
                search_val = request.session["search_val_session"]
            except:
                search_val = ""

        res = PostModel.objects.filter(status="published").filter(
            Q(title__icontains=search_val) | Q(body__icontains=search_val))

        posts = res

        tag = None
        if tag_slug:
            tag = Tag.objects.get(slug=tag_slug)
            posts = posts.filter(tags__in=[tag])

        page_num = request.GET.get("page", 1)
        # paginator = Paginator(posts, 15)
        paginator = Paginator(posts, 1)

        try:
            posts = paginator.page(page_num)
        except EmptyPage:
            paginator.page(1)
        except PageNotAnInteger:
            paginator.page(paginator.num_pages)

        _classy_poems = _CLASSY_POEMS

        context = {
            "posts": posts,
            "page": page_num,
            "tag": tag,
            "search_val": search_val,
            "classy_poems": _classy_poems,
        }

        return render(request, "posts/posts.html", context)


def postdetail_edit_view(request, pk, slug):
    post = get_object_or_404(PostModel, slug=slug, pk=pk)
    comments = CommentModel.objects.filter(post=post)

    if request.method == "POST":
        form = AddPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post.title = cd["title"]
            post.body = cd["body"]
            slug = str(post.author) + "-" + str(post.title) + \
                "-" + str(post.time_for_slg)
            post.slug = slugify(slug)
            post.status = "draft"
            post.save()
            # post.tags.all().delete()
            post.tags.add(str(post.title))
            post.tags.add(str(post.author))
            post.tags.add(str(post.time_for_slg))

            return redirect("users:user_detail_page")

    else:
        form = AddPostForm()

    context = {
        "post": post,
        "comments": comments,
        "form": form,
    }

    return render(request, "posts/edit-post.html", context)
