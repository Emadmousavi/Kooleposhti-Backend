from django.db import models
from accounts.models import Instructor, Student
from uuid import uuid4
from Kooleposhti import settings


class Promotion(models.Model):
    description = models.CharField(max_length=255)
    # course_set -> all courses promotions applied to
    discount = models.FloatField()


class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    image = models.ImageField(upload_to='static/images/course_images/', blank=True, default="static/images/no_photo.jpg")

    def __str__(self):
        return self.title




class Course(models.Model):
    '''
    ('title', 'description', 'price', 'last_update', 'instructor')
    '''
    category = models.ForeignKey(Category, related_name='courses', on_delete=models.CASCADE)
    # tags = models.ManyToManyField(Tag, blank=True)
    instructor = models.ForeignKey(Instructor, blank=True, related_name='courses', on_delete=models.CASCADE)
    students = models.ManyToManyField(Student, blank=True, related_name='courses')
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True, null=True, blank=True)
    image = models.ImageField(upload_to='static/images/course_images/', blank=True, default="static/images/no_photo.jpg")
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)  # 9999.99
    rate = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    rate_no = models.IntegerField(default=0)
    # first time we create Course django stores the current datetime
    last_update = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # enrollment_start_date = models.DateTimeField()
    # enrollment_end_date = models.DateTimeField()
    start_date = models.DateField(blank=True)
    end_date = models.DateField(blank=True)
    # start_class = models.DateTimeField()
    # end_class = models.DateTimeField()
    duration = models.DurationField()
    promotions = models.ManyToManyField(Promotion, blank=True)
    min_students = models.IntegerField(blank=True, default=1)
    max_students = models.IntegerField()
    min_age = models.IntegerField(default=1)
    max_age = models.IntegerField(default=18)

    def __str__(self):
        return self.title

    def is_enrolled(self, user):
        return self.students.filter(id=user.id).exists()

    def is_owner(self, user):
        return self.instructor == user

    @property
    def capacity(self):
        return self.max_students - len(self.students)

    def update_rate(self):
        self.rate_no = len(self.rates)
        self.rate = sum([rate_obj.rate for rate_obj in self.rates]) / self.rate_no
        



class Rate(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='rates')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='rates')
    rate = models.DecimalField(max_digits=2, decimal_places=1, default=0)

    def __str__(self):
        return f"{self.course__title} {self.rate}"



class Session(models.Model):
    course = models.ForeignKey(Course, blank=True, on_delete=models.CASCADE, related_name='sessions')
    # title = models.CharField()
    # student_no = models.IntegerField()
    # enrollment_start_date = models.DateTimeField()
    # enrollment_end_date = models.DateTimeField()
    # price = models.DecimalField(max_digits=6, decimal_places=2)  # 9999.99
    date = models.DateField()
    time = models.TimeField()
    # end_time = models.TimeField(blank=True)
    def __str__(self):
        return f"{self.course__title} {self.date} {self.time}"


class Comment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comments')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='comments')
    created_date = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    def __str__(self):
        return f"{self.course__title} {self.text}"


class Tag(models.Model):
    course = models.ForeignKey(Course, blank=True, on_delete=models.CASCADE, related_name='tags')
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.course__title} {self.name}"



class Chapter(models.Model):
    course = models.ForeignKey(Course, blank=True, on_delete=models.CASCADE, related_name='chapters')
    name = models.CharField(max_length=255)
    number = models.IntegerField(blank=True)
    # description = models.TextField(blank=True)
    # slug = models.SlugField(max_length=255, unique=True)
    # created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course__title} {self.name}"


class Goal(models.Model):
    course = models.ForeignKey(Course, blank=True, related_name='goals' , on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return f"{self.course__title} {self.text}"


class Prerequisite(models.Model):
    course = models.ForeignKey(Course, blank=True, related_name='prerequisites' , on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return f"{self.course__title} {self.text}"


class Order (models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed'),
    ]
    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    student = models.ForeignKey(Student, on_delete=models.PROTECT)


class OrderItem (models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)


class ShoppingCart(models.Model):  # Cart
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(
        ShoppingCart, on_delete=models.CASCADE, related_name='items')  # ShoppingCart.items
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = [
            ['cart', 'course'],
        ]


class Review(models.Model):
    '''
    fields = ('id', 'date', 'name', 'description', 'course')
    '''
    course = models.ForeignKey(
        Instructor, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)
