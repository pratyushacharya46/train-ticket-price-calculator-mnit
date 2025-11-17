"""Train class for managing train routes and pricing."""

from decimal import Decimal

from src.pricing_strategies import PricingStrategy
from src.types import CoachType, TicketType


class Train:
    def __init__(
        self,
        train_number: str,
        stations: list[str],
        pricing_strategy: PricingStrategy,
    ):
        self.train_number = train_number
        self.stations = stations
        self.pricing_strategy = pricing_strategy

    def calculate_ticket_price(
        self,
        ticket_type: TicketType,
        coach_type: CoachType,
        number_of_passengers: int,
        from_station: str,
        to_station: str,
    ) -> Decimal:
        """
        Calculate ticket price for this train.

        Args:
            ticket_type: Type of ticket (General or Tatkal)
            coach_type: Type of coach
            number_of_passengers: Number of passengers
            from_station: Starting station
            to_station: Destination station

        Returns:
            Total price for the tickets
        """
        return Decimal(0)
