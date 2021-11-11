from rest_framework import serializers
from rest_framework.utils import model_meta

from images.serializers import ProfileImageSerializer
from .models import User
from rest_framework import serializers
from .serializers import update_relation


class BaseUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    password = serializers.CharField(
        write_only=True, max_length=128, required=False)
    first_name = serializers.CharField(
        source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    phone_no = serializers.CharField(source='user.phone_no', required=False)
    birth_date = serializers.DateField(
        source='user.birth_date', required=False)
    roles = serializers.ReadOnlyField(
        source='user.get_user_roles', required=False)
    image = ProfileImageSerializer(source='user.image', required=False)

    class Meta:
        ref_name = None
        fields = ['id', 'username', 'email', 'password',
                  'first_name', 'last_name', 'phone_no', 'birth_date',
                  'roles', 'image']

    def set_password(self, instance, validated_data):
        if not 'password' in validated_data:
            return
        password = validated_data.pop('password')
        instance.user.set_password(password)
        instance.save()

    def set_image(self, instance, validated_data):
        image = validated_data.pop('image', None)
        image = ProfileImageSerializer(data=image)
        image.is_valid(raise_exception=True)
        image = image.save()
        instance.user.image = image
        instance.save()

    def update(self, instance, validated_data):
        self.set_image(instance, validated_data['user'])
        self.set_password(instance, validated_data)
        update_relation(instance, validated_data, 'user')
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        # m2m_fields = []
        # for attr, value in validated_data.items():
        #     if attr in info.relations and info.relations[attr].to_many:
        #         m2m_fields.append((attr, value))
        #     else:
        #         setattr(instance, attr, value)
        self.context.get('request').user = instance.user
        instance.save()

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        # for attr, value in m2m_fields:
        #     field = getattr(instance, attr)
        #     field.set(value)

        return instance


class UserSerializer(BaseUserSerializer):
    username = serializers.CharField(read_only=True, required=False)
    email = serializers.EmailField(read_only=True, required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    phone_no = serializers.CharField(required=False)
    birth_date = serializers.DateField(required=False)
    roles = serializers.ReadOnlyField(source='get_user_roles', required=False)
    image = ProfileImageSerializer(required=False)

    class Meta (BaseUserSerializer.Meta):
        model = User
        fields = BaseUserSerializer.Meta.fields
