from utils.fields import TagsField, CurrentModel
from user_profile.models import Rec, Collection
from rest_framework.serializers import ModelSerializer, HiddenField

class RecSerializer(ModelSerializer):
    author = TagsField()
    fandom = TagsField()
    warnings = TagsField()
    ship = TagsField()
    characters = TagsField()
    tags = TagsField()
    collection = HiddenField(default=CurrentModel())

    class Meta:
        model = Rec
        exclude = ["created", "deleted", "id"]
        # extra_kwargs = {'collection': {'write_only': True}}

class CollectionNameSerializer(ModelSerializer):
    class Meta:
        model = Collection
        fields = ["uid", "name"]