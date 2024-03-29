from django.db import models
from django.contrib.auth.models import User
from food.models import Food
from imagekit.models.fields import ProcessedImageField
from imagekit.processors import ResizeToFit, Adjust
from django.core.validators import MaxValueValidator
import os
import uuid

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('Recipe_photos', filename)

def did_get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('DidRecipe_photos', filename)


class RecipeCategory(models.Model):
	"""docstring for RecipeCategory"""

	name = models.CharField(max_length=200)
	brief = models.TextField(blank=True)
	parent = models.ForeignKey('self', null=True, blank=True)

	def __unicode__(self):
		return self.name

	@models.permalink
	def get_absolute_url(self):
		return ('recipe_category', (self.id, 'hot'))


class Recipe(models.Model):
	"""docstring for Recipe"""

	name = models.CharField(db_index=True, max_length=200)
	author = models.ForeignKey(User)
	date = models.DateField(auto_now_add=True)
	category = models.ManyToManyField(RecipeCategory, verbose_name=u'list of categories')
	brief = models.TextField()
	ingredients = models.ManyToManyField(Food, through='Amount', verbose_name=u"list of ingredients")

	cover_image = ProcessedImageField(upload_to=get_file_path, null=True, blank=True, verbose_name=u'Cover image',
						processors=[Adjust(contrast=1.2, sharpness=1.1),
            ResizeToFit(width=540,upscale=True)], format='JPEG', options={'quality': 90})

	tips = models.TextField(blank=True)
	did_num = models.PositiveIntegerField(default=0)
	like_num = models.PositiveIntegerField(default=0)
	view_num = models.PositiveIntegerField(default=0)
	trend_num = models.FloatField(default=0.0)
	today_view_num = models.PositiveIntegerField(default=0)

	prep_time = models.TimeField()
	cook_time = models.TimeField()

	cumulative_score = models.IntegerField(default=0)
	rating_num = models.IntegerField(default=0)

	def rating(self):
		result = float(self.cumulative_score)
		if self.rating_num == 0:
			return "0.0"
		result = result/self.rating_num
		return "%g" % round(result, 1)

	def rating_int(self):
		result = float(self.cumulative_score)
		if self.rating_num == 0:
			return 0
		result = result/self.rating_num
		return int(round(result))

	def __unicode__(self):
		return self.name

	@models.permalink
	def get_absolute_url(self):
		return ('recipe_detail', (), {'pk': self.id})

	class Meta:
		ordering = ['-view_num', '-like_num']


class DidRecipe(models.Model):
	"""docstring for DidRecipe"""
	recipe = models.ForeignKey(Recipe)
	user = models.ForeignKey(User)
	image = ProcessedImageField(upload_to=did_get_file_path, null=True, blank=True, verbose_name=u'Cover image',
						processors=[Adjust(contrast=1.2, sharpness=1.1),
            ResizeToFit(width=540,upscale=True)], format='JPEG', options={'quality': 90})
	comment = models.TextField()
	date = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return u"%s's %s" % (self.user.username, self.recipe.name)

	@models.permalink
	def get_absolute_url(self):
		return ('did_recipe_detail', (), {'pk': self.id})

	class Meta:
		ordering = ['recipe', '-date']

class Amount(models.Model):
	"""docstring for Amount"""
	
	ingredient = models.ForeignKey(Food)
	recipe = models.ForeignKey(Recipe)
	amount = models.CharField(max_length=50)
	must = models.BooleanField(default=False)

	def __unicode__(self):
		return u'Amount of %s in %s' % (self.ingredient.name, self.recipe.name)

	class Meta:
		ordering = ['recipe','-must']
		unique_together = ('recipe', 'ingredient')
		
class Step(models.Model):
	"""docstring for Steps"""

	recipe = models.ForeignKey(Recipe)
	step_num = models.PositiveIntegerField()
	description = models.CharField(max_length = 1000)
	step_image = ProcessedImageField(upload_to=get_file_path, null=True, blank=True, verbose_name=u'Step image',
						processors=[Adjust(contrast=1.2, sharpness=1.1),
            ResizeToFit(width=540,upscale=True)], format='JPEG', options={'quality': 80})

	def __unicode__(self):
		return u'Step %d of %s' % (self.step_num, self.recipe.name)

	class Meta:
		ordering = ['recipe', 'step_num']
		unique_together = ("recipe", "step_num")

class Vote(models.Model):
	"""Vote class, used for recommendation system """
	recipe = models.ForeignKey(Recipe)
	user = models.ForeignKey(User)
	score = models.PositiveSmallIntegerField(validators=[MaxValueValidator(5)])
	comment = models.TextField()
	date = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return u'Vote for %s from %s' %(self.recipe.name, self.user)

	class Meta:
		ordering = ['user', 'recipe',]
		unique_together = ("user", "recipe")
