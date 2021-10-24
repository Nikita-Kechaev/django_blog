from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Follow, Group, Post, User


def index(request):
    title = 'Последние обновления на сайте.'
    template = 'posts/index.html'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_list(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, 'posts/group_list.html', context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    post_title = post.text[:30]
    author_posts_count = post.author.posts.count()
    form = CommentForm(
        request.POST or None,
        files=request.FILES or None
    )
    comments = post.comments.all()
    context = {
        'post': post,
        'post_title': post_title,
        'author_posts_count': author_posts_count,
        'form': form,
        'comments': comments
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    user = request.user
    author = get_object_or_404(User, username=username)
    is_follow = False
    if user != author:
        is_follow = True
    following = False
    if user.is_authenticated:
        if user.follower.filter(author=author):
            following = True
    author_posts_list = author.posts.all()
    author_posts_list_count = author_posts_list.count()
    paginator = Paginator(author_posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'is_follow': is_follow,
        'following': following,
        'author': author,
        'author_posts_list_count': author_posts_list_count,
        'page_obj': page_obj
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    user = request.user
    form = PostForm(request.POST or None)
    if form.is_valid():
        form = form.save(commit=False)
        form.author = user
        form.save()
        return redirect('posts:profile', username=user)
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    if user != post.author:
        return redirect('posts:post_detail', post_id=post.id)
    is_edit = True
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.id)
    return render(request,
                  template,
                  {'form': form,
                   'is_edit': is_edit}
                  )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(
        request.POST or None
    )
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post.id)


@login_required
def follow_index(request):
    user = request.user
    title = 'Статьи авторов, на которых Вы подписаны.'
    template = 'posts/follow.html'
    following = Follow.objects.filter(user=user)
    authors_id = list(following.values_list('author_id'))
    post = Post.objects.filter(author_id__in=authors_id)
    paginator = Paginator(post, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    follower = user.follower.all()
    if user != author and author not in User.objects.filter(
        following__in=follower
    ):
        Follow.objects.create(
            user=user,
            author=author
        )
        return redirect('posts:profile', username=author)
    return redirect('posts:profile', username=author)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=user,
        author=author
    ).delete()
    return redirect('posts:profile', username=author)
