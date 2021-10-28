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
    author_follow = User.objects.get(username=username)
    follow = None
    if request.user in User.objects.all():
        user_follow = User.objects.get(username=request.user)
        number_follow = Follow.objects.filter(
            author=author_follow, user=user_follow
        ).count()
        if number_follow == 1:
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
    post_comments = post.comments.all()
    user = request.user
    username = post.author
    number_posts = username.posts.count()
    post_title = post.text[0:29]
    context = {
        'post_title': post_title,
        'post': post,
        'number_posts': number_posts,
        'user': user,
        'username': username,
        'comments': post_comments,
        'form_comment': CommentForm

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
    user_obj = get_object_or_404(User, username=request.user.username)
    print(request.user.username)
    user_following = user_obj.follower.all()
    print(user_following)
    authors = User.objects.filter(following__in=user_following)
    posts = Post.objects.filter(author__in=authors)
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
    user_follow = get_object_or_404(User, username=request.user)
    if author_follow != user_follow:
        Follow.objects.create(
            user=user_follow,
            author=author_follow
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    user_follow = get_object_or_404(User, username=request.user.username)
    author_follow = get_object_or_404(User, username=username)
    follow = get_object_or_404(
        Follow, author=author_follow.pk, user=user_follow.pk
    )
    follow.delete()
    return redirect('posts:profile', username=username)
