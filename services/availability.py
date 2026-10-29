def units_free(room, dates, bookings):
    taken = [
        b for b in bookings.for_room_type(room.id)
        if b.holds_inventory and b.dates.overlaps(dates)
    ]
    return room.total_units - len(taken)