"""Pricing strategies for train ticket calculation."""

from abc import ABC, abstractmethod
from decimal import Decimal

from src.types import CoachType, TicketType


class PricingStrategy(ABC):

    @abstractmethod
    def calculate_price(
        self,
        ticket_type: TicketType,
        coach_type: CoachType,
        number_of_passengers: int,
        from_station: str,
        to_station: str,
        stations: list[str],
    ) -> Decimal:
        pass


class FixPricingStrategy(PricingStrategy):
    """Fixed pricing strategy - price per station."""

    # Default pricing per station for General tickets
    DEFAULT_GENERAL_PRICING: dict[CoachType, Decimal] = {
        CoachType.AC_3: Decimal("50"),
        CoachType.SLEEPER: Decimal("30"),
        CoachType.AC_2: Decimal("70"),
        CoachType.AC_1: Decimal("100"),
        CoachType.GENERAL: Decimal("20"),
    }

    # Default pricing per station for Tatkal tickets
    DEFAULT_TATKAL_PRICING: dict[CoachType, Decimal] = {
        CoachType.AC_3: Decimal("100"),
        CoachType.SLEEPER: Decimal("50"),
        CoachType.AC_2: Decimal("140"),
        CoachType.AC_1: Decimal("200"),
        CoachType.GENERAL: Decimal("40"),
    }

    def __init__(
        self,
        general_pricing: dict[CoachType, Decimal] | None = None,
        tatkal_pricing: dict[CoachType, Decimal] | None = None,
    ):
        """
        Initialize with optional custom pricing.

        Args:
            general_pricing: Custom pricing per station for general tickets.
                           If None, uses default pricing.
            tatkal_pricing: Custom pricing per station for tatkal tickets.
                          If None, uses default pricing.
        """
        self.general_pricing = self.DEFAULT_GENERAL_PRICING.copy()
        self.tatkal_pricing = self.DEFAULT_TATKAL_PRICING.copy()

    def calculate_price(
        self,
        ticket_type: TicketType,
        coach_type: CoachType,
        number_of_passengers: int,
        from_station: str,
        to_station: str,
        stations: list[str],
    ) -> Decimal:
        """
        Calculate price based on number of stations.

        Formula: price_per_station * number_of_stations * number_of_passengers
        """

        from_index = stations.index(from_station)
        to_index = stations.index(to_station)

        # Calculate number of stations between from and to (exclusive)
        number_of_stations = abs(to_index - from_index)

        if ticket_type == TicketType.GENERAL:
            price_per_station = self.general_pricing[coach_type]
        else:
            price_per_station = self.tatkal_pricing[coach_type]

        total_price = price_per_station*Decimal(number_of_stations)*Decimal(number_of_passengers)

        return total_price


class DistanceBasedPricingStrategy(PricingStrategy):

    # Default multipliers
    DEFAULT_BASE_RATE_PER_KM = Decimal("1.0")

    DEFAULT_COACH_MULTIPLIER: dict[CoachType, Decimal] = {
        CoachType.AC_3: Decimal("1.5"),
        CoachType.SLEEPER: Decimal("1.0"),
        CoachType.AC_2: Decimal("2.0"),
        CoachType.AC_1: Decimal("3.0"),
        CoachType.GENERAL: Decimal("0.5"),
    }

    DEFAULT_TICKET_MULTIPLIER: dict[TicketType, Decimal] = {
        TicketType.GENERAL: Decimal("1.0"),
        TicketType.TATKAL: Decimal("2.0"),
    }

    def __init__(
        self,
        station_distances: list[tuple[str, Decimal]],
        base_rate_per_km: Decimal | None = None,
        coach_multiplier: dict[CoachType, Decimal] | None = None,
        ticket_multiplier: dict[TicketType, Decimal] | None = None,
    ):
        """
        Initialize with station distances and optional custom pricing.

        Args:
            station_distances: List of (station_name, distance_from_previous) tuples.
                              First station should have distance 0.
                              Example: [("Mumbai", 0), ("Surat", 300), ("Kota", 500)]
                              means Mumbai is start, Surat is 300km from Mumbai,
                              Kota is 500km from Surat (800km total from Mumbai).
            base_rate_per_km: Base rate per kilometer. If None, uses default.
            coach_multiplier: Multiplier for each coach type. If None, uses default.
            ticket_multiplier: Multiplier for each ticket type. If None, uses default.
        """
        self.cumulative_distances: dict[str, Decimal] = {}
        self.station_order: dict[str, int] = {}
        cumulative = Decimal("0")

        for index, (station, distance_from_prev) in enumerate(station_distances):
            cumulative += distance_from_prev
            self.cumulative_distances[station] = cumulative
            self.station_order[station] = index

        self.base_rate_per_km = (
            base_rate_per_km
            if base_rate_per_km is not None
            else self.DEFAULT_BASE_RATE_PER_KM
        )
        self.coach_multiplier = (
            coach_multiplier
            if coach_multiplier is not None
            else self.DEFAULT_COACH_MULTIPLIER.copy()
        )
        self.ticket_multiplier = (
            ticket_multiplier
            if ticket_multiplier is not None
            else self.DEFAULT_TICKET_MULTIPLIER.copy()
        )

    def calculate_price(
        self,
        ticket_type: TicketType,
        coach_type: CoachType,
        number_of_passengers: int,
        from_station: str,
        to_station: str,
        stations: list[str],
    ) -> Decimal:
        """
        Calculate price based on distance between stations.

        Formula: distance * base_rate * coach_multiplier * ticket_multiplier * passengers
        """
        # Get cumulative distances for both stations
        if from_station not in self.cumulative_distances:
            raise ValueError(f"Station not found: {from_station}")

        # Calculate distance between stations (no abs needed now)
        distance = abs(
            self.cumulative_distances[to_station]
            - self.cumulative_distances[from_station]
        )

        total_price = (
            distance
            *self.base_rate_per_km
            * self.coach_multiplier[coach_type]
            * self.ticket_multiplier[ticket_type]
            * Decimal(number_of_passengers)
        )

        return total_price


class PremiumStationPricingStrategy(PricingStrategy):
    """
    Premium Station Pricing Strategy - Higher pricing for premium stations.

    This strategy applies premium pricing when tickets are booked from or to
    designated premium stations (e.g., major metro cities, tourist destinations,
    or high-demand stations).

    PRICING LOGIC (To be implemented):
    ----------------------------------
    1. Base Calculation:
       - Uses distance-based pricing as the foundation
       - Formula: distance * base_rate * coach_multiplier * ticket_multiplier

    2. Premium Station Surcharge:
       - If from_station is premium: Add premium_surcharge_percentage to base price
       - If to_station is premium: Add premium_surcharge_percentage to base price
       - If both are premium: Add premium_surcharge_percentage twice (compounded)

    3. Premium Tiers:
       - TIER_1 (Metro cities): 50% surcharge (e.g., Mumbai, Delhi, Bangalore)
       - TIER_2 (Major cities): 30% surcharge (e.g., Pune, Jaipur, Ahmedabad)
       - TIER_3 (Tourist spots): 20% surcharge (e.g., Goa, Shimla, Manali)

    EXAMPLE CALCULATIONS:
    --------------------
    Scenario 1: Regular station to Regular station
    - Mumbai (non-premium) to Surat (non-premium): 300km
    - Base price: 300 * 1.0 * 1.5 (AC3) * 1.0 (General) = ₹450
    - Premium surcharge: 0%
    - Final price: ₹450

    Scenario 2: Premium TIER_1 station to Regular station
    - Mumbai (TIER_1, 50%) to Surat (non-premium): 300km
    - Base price: ₹450
    - Premium surcharge: 50% of ₹450 = ₹225
    - Final price: ₹450 + ₹225 = ₹675

    Scenario 3: Regular station to Premium TIER_2 station
    - Surat (non-premium) to Jaipur (TIER_2, 30%): 800km
    - Base price: 800 * 1.0 * 1.5 (AC3) * 1.0 (General) = ₹1200
    - Premium surcharge: 30% of ₹1200 = ₹360
    - Final price: ₹1200 + ₹360 = ₹1560

    Scenario 4: Premium TIER_1 to Premium TIER_1 (both premium)
    - Mumbai (TIER_1, 50%) to Delhi (TIER_1, 50%): 1400km
    - Base price: 1400 * 1.0 * 1.5 (AC3) * 1.0 (General) = ₹2100
    - From station surcharge: 50% of ₹2100 = ₹1050
    - To station surcharge: 50% of ₹2100 = ₹1050
    - Final price: ₹2100 + ₹1050 + ₹1050 = ₹4200

    Scenario 5: Premium TIER_1 to Premium TIER_2 (different tiers)
    - Mumbai (TIER_1, 50%) to Jaipur (TIER_2, 30%): 1200km
    - Base price: 1200 * 1.0 * 1.5 (AC3) * 1.0 (General) = ₹1800
    - From station surcharge: 50% of ₹1800 = ₹900
    - To station surcharge: 30% of ₹1800 = ₹540
    - Final price: ₹1800 + ₹900 + ₹540 = ₹3240

    INITIALIZATION PARAMETERS:
    -------------------------
    - station_distances: List of (station_name, distance_from_previous) tuples
    - premium_stations: Dict mapping station names to premium tier percentages
      Example: {
          "Mumbai": Decimal("0.50"),    # TIER_1: 50% surcharge
          "Delhi": Decimal("0.50"),     # TIER_1: 50% surcharge
          "Jaipur": Decimal("0.30"),    # TIER_2: 30% surcharge
          "Goa": Decimal("0.20")        # TIER_3: 20% surcharge
      }
    - base_rate_per_km: Base rate per kilometer (default: 1.0)
    - coach_multiplier: Multiplier for each coach type
    - ticket_multiplier: Multiplier for each ticket type (General/Tatkal)

    VALIDATION RULES:
    ----------------
    - Premium surcharge must be between 0% and 100% (0.0 to 1.0)
    - Station must exist in station_distances to be marked as premium
    - If station not in premium_stations dict, treat as regular (0% surcharge)
    - Reverse routes should raise ValueError (same as DistanceBasedPricingStrategy)

    USE CASES:
    ---------
    1. Dynamic pricing for high-demand routes
    2. Revenue optimization for metro city connections
    3. Seasonal pricing for tourist destinations
    4. Differential pricing based on station infrastructure quality

    TODO: Implement this strategy following the above specification
    """

    # Default multipliers (same as DistanceBasedPricingStrategy)
    DEFAULT_BASE_RATE_PER_KM = Decimal("1.0")

    DEFAULT_COACH_MULTIPLIER: dict[CoachType, Decimal] = {
        CoachType.AC_3: Decimal("1.5"),
        CoachType.SLEEPER: Decimal("1.0"),
        CoachType.AC_2: Decimal("2.0"),
        CoachType.AC_1: Decimal("3.0"),
        CoachType.GENERAL: Decimal("0.5"),
    }

    DEFAULT_TICKET_MULTIPLIER: dict[TicketType, Decimal] = {
        TicketType.GENERAL: Decimal("1.0"),
        TicketType.TATKAL: Decimal("2.0"),
    }

    def __init__(
        self,
        station_distances: list[tuple[str, Decimal]],
        premium_stations: dict[str, Decimal] | None = None,
        base_rate_per_km: Decimal | None = None,
        coach_multiplier: dict[CoachType, Decimal] | None = None,
        ticket_multiplier: dict[TicketType, Decimal] | None = None,
    ):
        """
        Initialize Premium Station Pricing Strategy.

        Args:
            station_distances: List of (station_name, distance_from_previous) tuples.
                              First station should have distance 0.
            premium_stations: Dict mapping station names to premium surcharge percentages.
                            Example: {"Mumbai": Decimal("0.50")} means 50% surcharge.
                            If None, no stations are premium.
            base_rate_per_km: Base rate per kilometer. If None, uses default (1.0).
            coach_multiplier: Multiplier for each coach type. If None, uses default.
            ticket_multiplier: Multiplier for each ticket type. If None, uses default.

        Raises:
            ValueError: If premium surcharge is not between 0.0 and 1.0
            ValueError: If premium station not in station_distances
        """
        pass

    def calculate_price(
        self,
        ticket_type: TicketType,
        coach_type: CoachType,
        number_of_passengers: int,
        from_station: str,
        to_station: str,
        stations: list[str],
    ) -> Decimal:
        """
        Calculate price with premium station surcharges.

        Formula:
        1. base_price = distance * base_rate * coach_multiplier * ticket_multiplier
        2. from_surcharge = base_price * premium_stations.get(from_station, 0)
        3. to_surcharge = base_price * premium_stations.get(to_station, 0)
        4. total_price = (base_price + from_surcharge + to_surcharge) * passengers

        Args:
            ticket_type: Type of ticket (General or Tatkal)
            coach_type: Type of coach
            number_of_passengers: Number of passengers
            from_station: Starting station
            to_station: Destination station
            stations: List of all stations on the route

        Returns:
            Total price including premium surcharges

        Raises:
            ValueError: If station not found
            ValueError: If reverse route (to_station comes before from_station)
        """
        pass
