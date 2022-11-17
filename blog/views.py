from django.shortcuts import render
from django.utils import timezone
from .models import Post, Comment
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm, CommentForm
from django.core.exceptions import PermissionDenied


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comment_set.all()
    return render(request, 'blog/post_detail.html', {"post": post, "comments": comments})

def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
        return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})
    
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    num_visits = request.session.get('num_visits', 0)
    num_visits += 1
    request.session['num_visits'] = num_visits
    return render(request, 'blog/post_list.html', {"posts": posts, "num_visits": num_visits})


def comment_new(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    post = get_object_or_404(Post, pk=pk)    
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post_detail', pk = post.pk)
    else:        
        form = CommentForm()
    return render(request, 'blog/comment_new.html', {'form': form})

def comment_edit(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user != comment.author:
        raise PermissionDenied
    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save()
            return redirect('post_detail', pk=comment.post.pk)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'blog/comment_edit.html', {'form': form})
