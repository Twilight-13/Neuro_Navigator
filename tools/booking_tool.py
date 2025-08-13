def get_booking_tool():
    def mock_booking(details):
        # Simulate API call for demo purposes
        return f"[BOOKED] {details} (mock booking confirmation: #ABC123)"
    return mock_booking
