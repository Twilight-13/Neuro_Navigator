import requests
import yfinance as yf
import os
import re


class FinanceTool:
    """Handles real-world price lookups (flights, hotels, daily costs, forex, stocks, currency normalization)."""

    def __init__(self):
        # Map symbols/names → ISO codes
        self.currency_map = {
            "$": "USD", "usd": "USD", "dollar": "USD",
            "rupee": "INR", "₹": "INR", "inr": "INR",
            "€": "EUR", "eur": "EUR", "euro": "EUR",
            "£": "GBP", "gbp": "GBP", "pound": "GBP",
            "¥": "JPY", "jpy": "JPY", "yen": "JPY"
        }

    # --- Detect currency from user text ---
    def detect_currency(self, text: str, default="USD"):
        """Detect currency and amount from text (supports symbols, names, short codes)."""
        text_low = text.lower().strip()

        # Extract numeric value
        amount = re.findall(r"[\d,.]+", text_low)
        amount = float(amount[0].replace(",", "")) if amount else None

        # Detect currency
        for k, v in self.currency_map.items():
            if k in text_low:
                return amount, v

        return amount, default

    # --- Amadeus: Get OAuth token ---
    def get_amadeus_token(self):
        url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": os.getenv("AMADEUS_CLIENT_ID"),
            "client_secret": os.getenv("AMADEUS_CLIENT_SECRET")
        }
        try:
            r = requests.post(url, data=data)
            r.raise_for_status()
            return r.json().get("access_token")
        except Exception:
            return None

    # --- Flights ---
    def get_flight_price(self, origin, destination, departure_date, return_date=None):
        token = self.get_amadeus_token()
        if not token:
            return "Flight price unavailable - Amadeus auth failed"

        url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "adults": 1,
            "currencyCode": "USD"
        }
        if return_date:
            params["returnDate"] = return_date

        try:
            r = requests.get(url, headers=headers, params=params)
            r.raise_for_status()
            data = r.json()
            return data["data"][0]["price"]["total"]
        except Exception:
            return "Flight price unavailable - check Amadeus API"

    # --- Helper: Get Booking.com dest_id ---
    def get_dest_id(self, city: str):
        url = "https://{}/v1/hotels/locations".format(
            os.getenv("RAPIDAPI_HOST", "booking-com15.p.rapidapi.com")
        )
        headers = {
            "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
            "X-RapidAPI-Host": os.getenv("RAPIDAPI_HOST", "booking-com15.p.rapidapi.com")
        }

        variations = [city, city.split(",")[0], "New Delhi"]

        for q in variations:
            try:
                params = {"name": q.strip(), "locale": "en-us"}
                r = requests.get(url, headers=headers, params=params)
                r.raise_for_status()
                data = r.json()

                if data and isinstance(data, list):
                    dest_id = data[0].get("dest_id")
                    if dest_id:
                        print(f"[get_dest_id] Found dest_id {dest_id} for query: {q}")
                        return dest_id
            except Exception as e:
                print(f"[get_dest_id] Error for query {q}:", e)

        print(f"[get_dest_id] No dest_id found for {city}")
        return None

    # --- Hotels ---
    def get_hotel_price(self, city, checkin, checkout):
        dest_id = self.get_dest_id(city)
        if not dest_id:
            return f"Hotel price unavailable for {city} (dest_id not found)"

        url = "https://booking-com.p.rapidapi.com/v1/hotels/search"
        headers = {
            "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
            "X-RapidAPI-Host": "booking-com.p.rapidapi.com"
        }
        params = {
            "dest_type": "city",
            "locale": "en-us",
            "order_by": "price",
            "checkin_date": checkin,
            "checkout_date": checkout,
            "dest_id": dest_id,
            "adults_number": 1,
            "units": "metric",
            "currency": "USD"
        }
        try:
            r = requests.get(url, headers=headers, params=params)
            r.raise_for_status()
            data = r.json()
            return data["result"][0]["price_breakdown"]["gross_price"]
        except Exception as e:
            print("[get_hotel_price] Error:", e)
            return f"Hotel price unavailable for {city}"

    # --- Daily living costs ---
    def get_city_cost(self, city):
        api_key = os.getenv("NUMBEO_API_KEY")
        if not api_key:
            return {"meal": 15.0, "transport": 10.0}

        url = f"https://www.numbeo.com/api/price_items?api_key={api_key}&query={city}"
        try:
            r = requests.get(url)
            r.raise_for_status()
            data = r.json()
            return {
                "meal": next((i["average_price"] for i in data["prices"] if "Meal" in i["item_name"]), 15.0),
                "transport": next((i["average_price"] for i in data["prices"] if "Taxi" in i["item_name"]), 10.0)
            }
        except Exception:
            return {"meal": 15.0, "transport": 10.0}

    # --- Forex / Currency conversion ---
    def convert_currency(self, amount, from_currency="USD", to_currency="INR"):
        try:
            ticker = f"{from_currency}{to_currency}=X"
            rate = yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1]
            return round(amount * rate, 2)
        except Exception:
            return "N/A"

    # --- Stocks / Crypto ---
    def get_stock_price(self, symbol: str):
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period="1d")
            if data.empty:
                return f"No data found for {symbol}"
            latest_price = round(data["Close"].iloc[-1], 2)
            return {"symbol": symbol, "price": latest_price}
        except Exception as e:
            return {"error": str(e)}

    def get_multiple_prices(self, symbols: list):
        return {s: self.get_stock_price(s) for s in symbols}
