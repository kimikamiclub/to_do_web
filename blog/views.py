from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from .models import Post, Comment, Profile, Category
from django.utils import timezone
from .forms import PostForm, CommentForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')

    if request.method == "POST":
        searched_post = request.POST.get('name', None)
        if searched_post:
            posts = posts.filter(title__contains=searched_post)
    else:
        category_id = request.GET.get('category_id', None)
        if category_id:
            posts = posts.filter(category_id=category_id)

    return render(request, 'blog/post_list.html', {"posts": posts})


def post_detail(request, pk):
    try:
        post = Post.objects.get(id=pk)
    except ObjectDoesNotExist:
        #TODO return custom 404 page
        raise Http404("object not found")

    return render(request, 'blog/post_detail.html', {'post': post})


@login_required
def post_new(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.category = Category.objects.get(pk=request.POST.get("category"))
            post.save()
            return redirect('post_detail', pk=post.pk)
        else:
            return render(request, 'blog/post_edit.html', {'form': form, 'categories': categories, 'statuses': Post.STATUS})

    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form, 'categories': categories})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    categories = Category.objects.all()
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            image = request.FILES.get("image", None)
            post.image = image if image else post.image
            post.author = request.user
            post.category = Category.objects.get(pk=request.POST.get("category"))
            post.save()
            return redirect('post_detail', pk=post.pk)
        else:
            return render(request, 'blog/post_edit.html', {'form': form, 'categories': categories})
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form, 'categories': categories})


@login_required
def post_draft_list(request):
    drafts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'drafts':drafts})


@login_required
def post_publish(request, pk):
    published_post = Post.objects.get(id=pk)
    published_post.publish()
    return redirect('post_list')


@login_required
def post_remove(request, pk):
    removed_post = get_object_or_404(Post, id=pk)
    removed_post.delete()
    return redirect('post_list')


def post_add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', pk=pk)
        else:
            return render(request, "blog/post_add_comment.html", {"form": form})
    else:
        form = CommentForm()
        return render(request, "blog/post_add_comment.html", {"form": form})


def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)


def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('post_detail', pk=comment.post.pk)


def registration(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.is_active = True
            new_user.save()
            profile = Profile.objects.create(user=new_user)
            return render(request, "registration/register_done.html", {'new_user': new_user})
        else:
            return render(request, "registration/registration.html", {'form': form})
    else:
        form = UserRegistrationForm()
        return render(request, 'registration/registration.html', {'form': form})


@login_required
def edit_profile(request):
    user = request.user
    if request.method == "POST":
        profile_form = ProfileEditForm(request.POST, instance=user.profile)
        user_form = UserEditForm(request.POST, instance=user)
        if profile_form.is_valid() and user_form.is_valid():
            photo = request.FILES.get('photo', None)
            profile_form.instance.photo = photo if photo else profile_form.instance.photo
            profile_form.save()
            user_form.save()
            return redirect('edit_profile')
        else:
            return render(
                request,
                'registration/profile_edit.html',
                {'user_form': user_form, 'profile_form': profile_form}
            )
    else:
        user_form = UserEditForm(instance=user)
        profile_form = ProfileEditForm(instance=user.profile)
    return render(
        request,
        'registration/profile_edit.html',
        {'user_form': user_form, 'profile_form': profile_form}
    )



