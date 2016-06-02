from rest_framework import serializers

from .models import Interaction, EmailInteraction


class EmailInteractionSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmailInteraction


class InteractionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Interaction

    def to_representation(self, obj):
        """
        Interactions are Polymorphic
        """
        if isinstance(obj, EmailInteraction):
            return EmailInteractionSerializer(obj, context=self.context).to_representation(obj)
        return serializers.ModelSerializer.to_representation(self, obj)
