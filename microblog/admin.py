# -*- coding: UTF-8 -*-
import datetime

from django import forms
from django.contrib import admin
from django.conf import settings

import models

class PostForm(forms.ModelForm):
    def clean(self):
        data = self.cleaned_data
        # mi assicuro che se una lingua è stata utilizzata i campi
        # headline, slug e summary devono essere riempiti
        # inoltre mi assicuro che almeno una lingua sia stata usata
        valid_langs = []
        language_fields = 'headline', 'slug', 'summary', 'body'
        needed_fields = set(('headline', 'slug', 'summary'))
        for l, lname in settings.LANGUAGES:
            lfield = []
            for fname in language_fields:
                key = fname + '_' + l
                if data[key]:
                    lfield.append(fname)
            if lfield:
                if needed_fields.intersection(set(lfield)) != needed_fields:
                    raise forms.ValidationError('Se utilizzi una lingua i campi "headline", "slug" e "summary" sono obbligatori')
                else:
                    valid_langs.append(l)

        if not valid_langs:
            raise forms.ValidationError('Devi usare almeno una lingua')
            
        return data

class PostAdmin(admin.ModelAdmin):
    form = PostForm
    date_hierarchy = 'date'
    list_display = ('headline', 'date', 'author', 'status')

    def headline(self, obj):
        contents = dict((c.language, c) for c in obj.postcontent_set.all())
        for l, lname in settings.LANGUAGES:
            try:
                content = contents[l]
            except KeyError:
                continue
            if content.headline:
                return content.headline
        else:
            return '[No headline]'

    def get_fieldsets(self, request, obj=None, **kwargs):
        fieldsets = [
            (None, {
                'fields': ('date', 'author', 'status', 'tags', 'allow_comments')
            })
        ]
        prepopulated_fields = {}
        lang_fieldsets = {}
        for l, lname in settings.LANGUAGES:
            f = (lname, { 'fields': [] } )
            lang_fieldsets[l] = f[1]
            fieldsets.append(f)
            prepopulated_fields['slug_' + l] = ('headline_' + l,)
        self.prepopulated_fields = prepopulated_fields

        form = self.get_form(request, obj)
        for name in form.base_fields:
            if '_' not in name:
                continue
            l = name.rsplit('_', 1)[1]
            if len(l) > 3:
                # houch, allow_comments ha l'_
                continue
            lang_fieldsets[l]['fields'].append(name)
        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        form = super(PostAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            contents = dict((c.language, c) for c in obj.postcontent_set.all())
        def getContent(lang, field):
            try:
                return getattr(contents[lang], field, '')
            except KeyError:
                return ''
        # a differenza delle deadline qui devo aggiungere 4 campi
        #   headline
        #   slug
        #   summary
        #   body
        for l, _ in settings.LANGUAGES:
            fields = {
                'headline': forms.CharField(required = False, max_length = 200),
                'slug': forms.CharField(required = False, max_length = 50),
                'summary': forms.CharField(required = False, widget = forms.Textarea),
                'body': forms.CharField(required = False, widget = forms.Textarea),
            }
            for k in 'headline', 'slug', 'summary', 'body':
                f = fields[k]
                if obj:
                    f.initial = getContent(l, k)
                form.base_fields[k + '_' + l] = f
        # un po' di valori di default sensati
        form.base_fields['date'].initial = datetime.datetime.now()
        form.base_fields['author'].initial = request.user.id
        return form

    def save_model(self, request, obj, form, change):
        obj.save()
        data = form.cleaned_data
        fields = ('headline', 'slug', 'summary', 'body')
        for l, _ in settings.LANGUAGES:
            if change:
                try:
                    instance = models.PostContent.objects.get(post = obj, language = l)
                except models.PostContent.DoesNotExist:
                    instance = models.PostContent()
            else:
                instance = models.PostContent()
            if not instance.id:
                instance.post = obj
                instance.language = l
            for f in fields:
                key = f + '_' + l
                setattr(instance, f, data.get(key, ''))
            instance.save()

admin.site.register(models.Post, PostAdmin)
