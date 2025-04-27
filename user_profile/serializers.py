from rest_framework import serializers
from django.core.validators import RegexValidator
from authentication.models import Reader
from user_profile.models import Collection, Rec
from user_profile.utils import CODE_REGEX
from public.models import Saved
from utils import fields as utils_fields
from utils import serializers as utils_serializers
import re
from bs4 import BeautifulSoup
import nh3

class ReaderSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    collections = utils_fields.NestedListField(
        child=utils_serializers.CollectionNameSerializer,
        source="reader_collection",
        read_only=True,
        filter = dict(deleted=False, reader__user__is_active=True)
    )
    class Meta:
        model = Reader
        fields = ["uid", "username", "bio", "avatar", "collections", "highlight"]
        read_only_fields = ['uid', "username", "collections"]

class CollectionSerializer(serializers.ModelSerializer):
    reader = serializers.HiddenField(default=utils_fields.CurrentReader())
    recs = utils_fields.NestedListField(
        child = utils_serializers.RecSerializer,
        source = "collection_recs",
        read_only = True,
        paginated = 15,
        filter = dict(deleted=False, collection__reader__user__is_active=True)
    )
    class Meta:
        model = Collection
        exclude = ["created", "deleted"]
        read_only_fields = ["uid", "recs", "private", "fandom", "ship", "warnings", "tags", "chapters", "summary"]
        extra_kwargs = {'reader': {'write_only': True}}
        
class ToggleSerializer(serializers.Serializer):
    toggle = serializers.ChoiceField(["private", "fandom", "ship", "warnings", "tags", "chapters", "summary"])

    def save(self, **kwargs):
        collection = self.context["view"].get_object()
        field = self.validated_data["toggle"]
        field_value = getattr(collection, field)
        setattr(collection, field, not field_value)
        collection.save()

        return collection

class PrepareRecSerializer(serializers.Serializer):
    notes = serializers.CharField(allow_null=True, required=False)
    code = serializers.CharField(required=True, validators=[RegexValidator(CODE_REGEX)])
    
    def validate_code(self, value):
        regex = re.search(CODE_REGEX, value)
        
        if not regex:
            raise ValueError("Invalid code")
        if len(value) != regex.end():
            raise ValueError("Invalid code")

        regex_keys = list(regex.groupdict().keys())
        if len(regex_keys) < 8:
            raise ValueError("Invalid code")
        # required groups
        for key in ["url", "title", "chapters", "rating", "words", "warnings", "fandom", "author"]:
            if key not in regex_keys:
                raise ValueError("Invalid code")
        return value
    
    def format_code(self):
        regex = re.search(CODE_REGEX, self.data["code"])
        content = regex.groupdict()
        keys = list(content.keys())
        rec_data = dict(notes = self.data["notes"])

        for key in keys:
            if key == "url":
                soup = BeautifulSoup(regex.group(key), 'html.parser')
                rec_data["link"] = soup.a["href"]
            if key in ["title", "chapters", "rating", "words"]:
                rec_data[key] = nh3.clean(regex.group(key), tags={""})
            if key in ["author", "fandom", "warnings", "ship", "characters", "tags"]:
                if regex.group(key):
                    rec_data[key] = nh3.clean(regex.group(key), tags={""})
        return rec_data
    
    def save(self):
        data = self.format_code()
        serializer = utils_serializers.RecSerializer(data=data, context=self.context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer

class EditRecSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rec
        fields = ["notes"]

class SavedSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="rec.title")
    author = utils_fields.TagsField(source="rec.author")
    fandom = utils_fields.TagsField(source="rec.fandom")
    ship = utils_fields.TagsField(source="rec.ship")
    summary = serializers.CharField(source="rec.title")
    collection = serializers.CharField(source="rec.collection.name")
    maker = serializers.CharField(source="rec.collection.reader.user.username")
    notes = serializers.CharField(source="rec.notes")
    link = serializers.URLField(source="rec.link")

    class Meta:
        model = Saved
        exclude = ["saved_by", "created", "deleted", "rec", "id"]
        read_only_fields = ["title", "author", "fandom", "ship", "summary", "collection", "maker", "notes", "link", "uid"]