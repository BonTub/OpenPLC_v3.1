def edit_profile(request):
    user = User.objects.get(pk=request.session['userid'])
    form = EditProfileForm(request.POST, obj=user)

    if request.POST and form.validate():
        form.populate_obj(user)
        user.save()
        return redirect('/home')
    return render_to_response('edit_profile.html', form=form)
