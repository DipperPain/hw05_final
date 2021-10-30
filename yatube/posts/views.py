from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import Post, User, Follow
from .models import Group
from .forms import PostForm, CommentForm
from django.core.paginator import Paginator
from django.urls import reverse


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    page_number = request.GET.get('page')
    page_obj = Paginator(posts_list, 10).get_page(page_number)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    group_html = 'posts/group_list.html'
    return render(request, group_html, context)


def index(request):
    post_list = Post.objects.all()
    # Если порядок сортировки определен в классе Meta модели,
    # запрос будет выглядить так:
    # post_list = Post.objects.all()
    # Показывать по 10 записей на странице.
    paginator = Paginator(post_list, 10)

    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')

    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    # Отдаем в словаре контекста
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    number_posts = author.posts.count()
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    author_follow = get_object_or_404(User, username=username)
    follow = None
    if request.user.is_authenticated:
        follow_exist = Follow.objects.filter(
            author=author_follow, user=request.user
        ).exists()
        if follow_exist:
            follow = 'following'
        else:
            follow = None
    context = {
        'page_obj': page_obj,
        'number_posts': number_posts,
        'author': author,
        'following': follow
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    user = request.user
    username = post.author
    form_comment = CommentForm(request.POST or None)
    number_posts = username.posts.count()
    post_title = post.text[0:29]
    context = {
        'post_title': post_title,
        'post': post,
        'number_posts': number_posts,
        'user': user,
        'username': username,
        'comments': comments,
        'form_comment': form_comment,

    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    author_user = request.user.username
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(reverse(
            'posts:profile', kwargs={'username': f'{author_user}'})
        )
    context = {'form': form}
    return render(request, 'posts/post_create.html', context)


@login_required
def post_edit(request, post_id):
    is_edit = 'is_edit'
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if request.method == 'POST' and form.is_valid():
        post.save()
        return redirect(reverse(
            'posts:post_detail', kwargs={'post_id': f'{post.pk}'})
        )
    context = {
        'form': form,
        'is_edit': is_edit,
        'post': post
    }

    return render(request, 'posts/post_create.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)

    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')

    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    # Отдаем в словаре контекста
    context = {
        'page_obj': page_obj,
    }

    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора

    author_follow = get_object_or_404(User, username=username)
    if author_follow != request.user:
        Follow.objects.get_or_create(
            user=request.user,
            author=author_follow
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    follow = Follow.objects.filter(
        author__username=username, user=request.user
    )
    follow.delete()
    return redirect('posts:profile', username=username)
