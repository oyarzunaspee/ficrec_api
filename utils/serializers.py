from utils.fields import TagsField, CurrentModel
from user_profile.models import Rec, Collection
from rest_framework.serializers import ModelSerializer, HiddenField, SerializerMethodField

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
    recs = SerializerMethodField("rec_count")
    
    class Meta:
        model = Collection
        fields = ["uid", "name", "private", "recs"]

    def rec_count(self, instance):
        return instance.collection_recs.count()