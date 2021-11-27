from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet
from .models import *
from decimal import Decimal
from accounts.models import Instructor
from djoser.serializers import UserSerializer as BaseUserSerializer
from accounts.serializers.instructor_serializer import InstructorSerializer
import jdatetime
import jalali_date
from datetime import date, datetime, time, timedelta
import base64
import os


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = '__all__'


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'

    def create(self, validated_data):
        # course = validated_data.pop('course')
        course_pk = self.context['course']
        course = Course.objects.get(pk=course_pk)
        date = validated_data['date']
        new_time = datetime.combine(
            date.today(), validated_data['start_time']) + timedelta(minutes=course.duration)
        end_time = new_time.time()
        day = date.day
        month = Session.MonthNames[date.month - 1][1]
        week = jdatetime.date(date.year, date.month, date.day).weekday()
        week_day = Session.WeekNames[week][1]
        return Session.objects.create(course=course, day=day, month=month,
                                      week_day=week_day, end_time=end_time, **validated_data)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

    # def create(self, validated_data):
    #     request = self.context.get("request")
    #     student = request.user
    #     return Comment.objects.create(student=student, **validated_data)


class CategorySerializer(serializers.ModelSerializer):
    # courses = CourseSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = '__all__'
        # fields = ['title', 'slug', 'image', 'courses']


class InstructorCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'image', 'start_date',
                  'end_date', 'max_students']


class CourseSerializer(serializers.ModelSerializer):
    instructor = InstructorSerializer(read_only=True)
    # category = CategorySerializer(many=True)
    # students = StudentSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    goals = GoalSerializer(many=True, read_only=True)
    sessions = SessionSerializer(many=True)

    class Meta:
        model = Course
        fields = ('id', 'created_at', 'categories', 'instructor',
                  'duration', 'title', 'image', 'description',
                  'price', 'rate', 'rate_no', 'link', 'min_students', 
                  'max_students', 'capacity', 'min_age', 'max_age',
                  'tags', 'goals', 'sessions', 'comments')
    # instructor = serializers.HyperlinkedRelatedField(
    #     queryset=Instructor.objects.all(), view_name='instructor-detail')
        new_price = serializers.SerializerMethodField(
            method_name='calculate_new_price')

    def calculate_new_price(self, course: Course):
        return course.price * Decimal(1.1)

    def create(self, validated_data):
        request = self.context.get("request")
        sessions_data = validated_data.pop('sessions')
        validated_data['instructor'] = request.user.instructor
        validated_data['start_date'] = sessions_data[0]['date']
        validated_data['end_date'] = sessions_data[-1]['date']
        validated_data['capacity'] = validated_data['max_students']

        return super().create(validated_data)

        # instructor = request.user.instructor
        # sessions_data = validated_data.pop('sessions')
        # start_date = sessions_data[0]['date']
        # end_date = sessions_data[-1]['date']
        # capacity = validated_data['max_students']
        # validated_data['course'] = Course.objects.create(instructor=instructor, start_date=start_date, end_date=end_date,
        #                                capacity=capacity, **validated_data)

    def update(self, instance, validated_data):
        sessions_data = validated_data.pop('sessions', [])
        if len(sessions_data):
            validated_data['start_date'] = sessions_data[0]['date']
            validated_data['end_date'] = sessions_data[-1]['date']
        capacity = instance.capacity + \
            validated_data.get(
                'max_students', instance.max_students) - instance.max_students
        if capacity < 0:
            self.fail("course remaining capacity should not be negative")
        validated_data['capacity'] = capacity

        return super().update(instance, validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('id', 'date', 'name', 'description')

    def create(self, validated_data):
        course_id = self.context['course_id']
        return Review.objects.create(
            course_id=course_id,
            **validated_data
        )


class SimpleCourseSerializer():
    # Basic info for Cart item
    class Meta:
        model = Course
        fields = ['id', 'title', 'price']


class CartItemSerializer(serializers.ModelSerializer):
    course = SimpleCourseSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.course.price

    class Meta:
        model = CartItem
        fields = ['id', 'course', 'quantity', 'total_price']


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart: ShoppingCart):
        return sum([item.quantity*item.course.price for item in cart.items.all()])

    class Meta:
        model = ShoppingCart
        fields = ['id', 'items', 'total_price']
