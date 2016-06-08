from random import randint
from django.template.defaultfilters import linebreaks, strip_tags
from rest_framework import serializers

from .models import (
    Interaction, PhoneInteraction, MeetingInteraction, EmailInteraction)


class IconographicInteractionSerializer(serializers.ModelSerializer):

    icon = serializers.SerializerMethodField()
    body_html = serializers.SerializerMethodField()

    def get_icon(self, obj):
        return self.__class__.__name__.replace(
            "InteractionSerializer", "").lower()

    def get_body_html(self, obj):
        r = getattr(obj, "notes", getattr(obj, "body", None))
        return linebreaks(r)


class PhoneInteractionSerializer(IconographicInteractionSerializer):

    class Meta:
        model = PhoneInteraction


class MeetingInteractionSerializer(IconographicInteractionSerializer):

    class Meta:
        model = MeetingInteraction


class EmailInteractionSerializer(IconographicInteractionSerializer):

    class Meta:
        model = EmailInteraction

    def get_body_html(self, obj):
        standin = str(randint(1000000, 999999999))
        return linebreaks(strip_tags(obj.body.replace(
            "\n\n", standin).replace("\n", " ").replace(standin, "\n\n")))


class InteractionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Interaction

    def to_representation(self, obj):
        """
        Interactions are Polymorphic
        """
        if isinstance(obj, PhoneInteraction):
            return PhoneInteractionSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, MeetingInteraction):
            return MeetingInteractionSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, EmailInteraction):
            return EmailInteractionSerializer(
                obj, context=self.context).to_representation(obj)
        return serializers.ModelSerializer.to_representation(self, obj)
