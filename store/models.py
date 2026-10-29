from django.db import models


class OwnerModel(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=200)


class PropertyModel(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    owner = models.ForeignKey(OwnerModel, on_delete=models.CASCADE, related_name='properties')
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100, db_index=True)
    locality = models.CharField(max_length=100, blank=True)
    star_rating = models.PositiveSmallIntegerField()
    amenities = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'id']


class RoomTypeModel(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    property = models.ForeignKey(PropertyModel, on_delete=models.CASCADE, related_name='room_types')
    name = models.CharField(max_length=100)
    capacity = models.PositiveSmallIntegerField()
    total_units = models.PositiveIntegerField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'id']


class BookingModel(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    property = models.ForeignKey(PropertyModel, on_delete=models.CASCADE)
    room_type = models.ForeignKey(RoomTypeModel, on_delete=models.CASCADE)
    guests = models.PositiveSmallIntegerField()
    check_in = models.DateField()
    check_out = models.DateField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'id']
        indexes = [models.Index(fields=['room_type', 'check_in', 'check_out'])]


class PaymentModel(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    booking = models.ForeignKey(BookingModel, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20)
    status = models.CharField(max_length=10)
    reference = models.CharField(max_length=50, blank=True)
    idempotency_key = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
