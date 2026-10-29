from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers


def parse(serializer_class, data):
    serializer = serializer_class(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


class OwnerInput(serializers.Serializer):
    name = serializers.CharField(allow_blank=True)


class RoomTypeInput(serializers.Serializer):
    name = serializers.CharField(allow_blank=True)
    capacity = serializers.IntegerField()
    total_units = serializers.IntegerField()
    base_price = serializers.DecimalField(max_digits=10, decimal_places=2)


class PropertyInput(serializers.Serializer):
    name = serializers.CharField(allow_blank=True)
    city = serializers.CharField(allow_blank=True)
    locality = serializers.CharField(allow_blank=True, required=False, default='')
    star_rating = serializers.IntegerField()
    amenities = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    room_types = RoomTypeInput(many=True)


class OwnerOutput(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    property_ids = serializers.ListField(child=serializers.CharField())


class RoomTypeOutput(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    capacity = serializers.IntegerField()
    total_units = serializers.IntegerField()
    base_price = serializers.DecimalField(max_digits=10, decimal_places=2)


class PropertyOutput(serializers.Serializer):
    id = serializers.CharField()
    owner_id = serializers.CharField()
    name = serializers.CharField()
    city = serializers.CharField()
    locality = serializers.CharField()
    star_rating = serializers.IntegerField()
    amenities = serializers.SerializerMethodField()
    room_types = RoomTypeOutput(many=True)

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_amenities(self, prop):
        return sorted(prop.amenities)
    
class SearchQuery(serializers.Serializer):
    city = serializers.CharField(allow_blank=True)
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    guests = serializers.IntegerField()
    locality = serializers.CharField(allow_blank=True, required=False, default='')


class SearchResultOutput(serializers.Serializer):
    property_id = serializers.CharField()
    name = serializers.CharField()
    city = serializers.CharField()
    star_rating = serializers.IntegerField()
    room_type_id = serializers.CharField()
    room_type = serializers.CharField()
    units_free = serializers.IntegerField()
    price_per_night = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2)


class BookingInput(serializers.Serializer):
    property_id = serializers.CharField()
    room_type_id = serializers.CharField()
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    guests = serializers.IntegerField()


class BookingOutput(serializers.Serializer):
    id = serializers.CharField()
    property_id = serializers.CharField()
    room_type_id = serializers.CharField()
    guests = serializers.IntegerField()
    check_in = serializers.DateField(source='dates.check_in')
    check_out = serializers.DateField(source='dates.check_out')
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    status = serializers.CharField(source='status.value')


class CancellationOutput(serializers.Serializer):
    booking_id = serializers.CharField(source='booking.id')
    status = serializers.CharField(source='booking.status.value')
    refund = serializers.DecimalField(max_digits=12, decimal_places=2)


class PaymentInput(serializers.Serializer):
    method = serializers.CharField(allow_blank=True)
    details = serializers.DictField(child=serializers.CharField())
    idempotency_key = serializers.CharField(allow_blank=True)


class PaymentOutput(serializers.Serializer):
    payment_id = serializers.CharField(source='payment.id')
    status = serializers.CharField(source='payment.status.value')
    reference = serializers.CharField(source='payment.reference')
    booking_status = serializers.CharField(source='booking.status.value')


class ErrorOutput(serializers.Serializer):
    error = serializers.CharField()
    details = serializers.DictField(required=False)


class SearchResponse(serializers.Serializer):
    results = SearchResultOutput(many=True)
