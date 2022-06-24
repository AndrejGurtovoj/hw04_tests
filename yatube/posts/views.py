from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .models import Post, Group, User
from .forms import PostForm


def page(request, posts):
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    templates = 'posts/index.html'
    posts = Post.objects.all()
    page_obj = page(request, posts)
    context = {
        'page_obj': page_obj,

    }
    return render(request, templates, context)


def group_posts(request, slug):
    templates = 'posts/group_list.html'
    posts = Post.objects.all()
    page_obj = page(request, posts)
    group = get_object_or_404(Group, slug=slug)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, templates, context)


def profile(request, username):
    template = "posts/profile.html"
    author = get_object_or_404(User, username=username)
    posts = author.posts.all().order_by("-pub_date")
    page_obj = page(request, posts)
    context = {
        'page_obj': page_obj,
        'author': author,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = "posts/post_detail.html"
    post = Post.objects.get(id=post_id)
    post_count = Post.objects.filter(author=post.author).count()
    context = {
        'post': post,
        'post_count': post_count,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post.objects.select_related('author'), pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    if request.user == post.author:
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)

        return render(request, 'posts/create_post.html',
                      {'form': form, 'is_edit': True})

    return redirect('posts:post_detail', post_id=post_id)
