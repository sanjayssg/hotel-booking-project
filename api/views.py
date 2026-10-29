from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from api import container
from api.serializers import (
    BookingInput, BookingOutput, CancellationOutput, ErrorOutput, OwnerInput, OwnerOutput,
    PaymentInput, PaymentOutput, PropertyInput, PropertyOutput,
    SearchQuery, SearchResponse, SearchResultOutput, parse,
)
from domain.dates import DateRange
from domain.filters import build_filters
from services.property_service import RoomTypeSpec

BAD_REQUEST = {400: ErrorOutput}
NOT_FOUND = {404: ErrorOutput}
CONFLICT = {409: ErrorOutput}

FILTER_PARAMETERS = [
    OpenApiParameter('min_price', str, description='Lowest nightly price, inclusive'),
    OpenApiParameter('max_price', str, description='Highest nightly price, inclusive'),
    OpenApiParameter('amenities', str, description='Comma separated, every one must be present'),
    OpenApiParameter('min_stars', int, description='Lowest star rating, inclusive'),
]


class OwnerList(APIView):
    @extend_schema(request=OwnerInput, responses={201: OwnerOutput, **BAD_REQUEST},
                   summary='Register an owner')
    def post(self, request):
        data = parse(OwnerInput, request.data)
        owner = container.property_service.register_owner(data['name'])
        return Response(OwnerOutput(owner).data, status=201)


class OwnerProperties(APIView):
    @extend_schema(request=PropertyInput,
                   responses={201: PropertyOutput, **BAD_REQUEST, **NOT_FOUND},
                   summary='Add a property, with its room types, to an owner')
    def post(self, request, owner_id):
        data = parse(PropertyInput, request.data)
        rooms = [RoomTypeSpec(**room) for room in data.pop('room_types')]
        prop = container.property_service.add_property(owner_id, room_types=rooms, **data)
        return Response(PropertyOutput(prop).data, status=201)


class PropertyDetail(APIView):
    @extend_schema(responses={200: PropertyOutput, **NOT_FOUND}, summary='Read a property')
    def get(self, request, property_id):
        prop = container.property_service.get_property(property_id)
        return Response(PropertyOutput(prop).data)


class PropertySearch(APIView):
    @extend_schema(parameters=[SearchQuery, *FILTER_PARAMETERS],
                   responses={200: SearchResponse, **BAD_REQUEST},
                   summary='Find room types that are free for the dates')
    def get(self, request):
        query = parse(SearchQuery, request.query_params)
        dates = DateRange(query['check_in'], query['check_out'])
        results = container.search_service.search(
            query['city'], dates, query['guests'],
            filters=build_filters(request.query_params),
            locality=query['locality'],
        )
        return Response({'results': SearchResultOutput(results, many=True).data})


class BookingList(APIView):
    @extend_schema(request=BookingInput,
                   responses={201: BookingOutput, **BAD_REQUEST, **NOT_FOUND, **CONFLICT},
                   summary='Book a room type and hold it until it is paid')
    def post(self, request):
        data = parse(BookingInput, request.data)
        dates = DateRange(data['check_in'], data['check_out'])
        booking = container.booking_service.book(
            data['property_id'], data['room_type_id'], dates, data['guests'])
        return Response(BookingOutput(booking).data, status=201)


class BookingDetail(APIView):
    @extend_schema(responses={200: BookingOutput, **NOT_FOUND}, summary='Read a booking')
    def get(self, request, booking_id):
        booking = container.booking_service.get_booking(booking_id)
        return Response(BookingOutput(booking).data)


class BookingCancel(APIView):
    @extend_schema(request=None, responses={200: CancellationOutput, **NOT_FOUND, **CONFLICT},
                   summary='Cancel a booking and get the refund amount')
    def post(self, request, booking_id):
        result = container.cancellation_service.cancel(booking_id)
        return Response(CancellationOutput(result).data)


class BookingPay(APIView):
    @extend_schema(request=PaymentInput,
                   responses={200: PaymentOutput, **BAD_REQUEST, **NOT_FOUND, **CONFLICT},
                   summary='Pay for a booking (a declined payment is still a 200)')
    def post(self, request, booking_id):
        data = parse(PaymentInput, request.data)
        result = container.payment_service.pay(
            booking_id, data['method'], data['details'], data['idempotency_key'])
        return Response(PaymentOutput(result).data)
