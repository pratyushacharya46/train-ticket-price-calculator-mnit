"""Ticket price calculator for managing multiple trains."""

from decimal import Decimal

from src.train import Train
from src.types import CoachType, TicketType


class TicketPriceCalculator:
    """Calculator for ticket prices across multiple trains."""

    def __init__(self, trains: list[Train]):
        self.trains: dict[str, Train] = {train.train_number: train for train in trains}

    def calculate(
        self,
        train_number: str,
        number_of_passengers: int,
        from_station: str,
        to_station: str,
        coach_type: CoachType,
        ticket_type: TicketType,
    ) -> Decimal:
        """
        Calculate ticket price for a specific train.

        Args:
            train_number: Train number to calculate price for
            number_of_passengers: Number of passengers
            from_station: Starting station
            to_station: Destination station
            coach_type: Type of coach
            ticket_type: Type of ticket (defaults to General)

        Returns:
            Total price for the tickets

        Raises:
            ValueError: If train not found or invalid route
        """

        train = self.trains[train_number]
        return train.calculate_ticket_price(
            ticket_type=ticket_type,
            coach_type=coach_type,
            number_of_passengers=number_of_passengers,
            from_station=from_station,
            to_station=to_station,
        )
