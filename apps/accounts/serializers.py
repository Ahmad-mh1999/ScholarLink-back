from rest_framework import serializers
from .models import User, Expertise


class ExpertiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expertise
        fields = ['id', 'title', 'description', 'icon']


class UserSerializer(serializers.ModelSerializer):
    expertise = ExpertiseSerializer(many=True, read_only=True)
    posts_count = serializers.ReadOnlyField()
    points = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'avatar', 'bio', 'institution', 'field_of_study',
            'academic_status', 'location', 'title', 'orcid_id',
            'website', 'expertise', 'date_joined',
            'role', 'is_staff', 'is_active', 'posts_count', 'points'
        ]
        read_only_fields = ['date_joined']

    def get_points(self, obj):
        if hasattr(obj, 'points'):
            return {'total': obj.points.total}
        return {'total': 0}


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)
    institution = serializers.CharField(required=True, allow_blank=False, error_messages={
        'required': 'Institution is required.',
        'blank': 'Institution cannot be blank.'
    })
    field_of_study = serializers.CharField(required=True, allow_blank=False, error_messages={
        'required': 'Field of study is required.',
        'blank': 'Field of study cannot be blank.'
    })

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password2', 'institution',
            'field_of_study', 'academic_status'
        ]

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('Passwords do not match.')
        
        # Validate institution is not empty or just whitespace
        institution = data.get('institution', '').strip()
        if not institution:
            raise serializers.ValidationError({'institution': 'Institution is required.'})
        
        # Validate field_of_study is not empty or just whitespace
        field_of_study = data.get('field_of_study', '').strip()
        if not field_of_study:
            raise serializers.ValidationError({'field_of_study': 'Field of study is required.'})
        
        # Strip whitespace from institution and field_of_study
        data['institution'] = institution
        data['field_of_study'] = field_of_study
        
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user