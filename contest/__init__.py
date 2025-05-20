from otree.api import (
    BaseConstants,
    BaseGroup,
    BasePlayer,
    BaseSubsession,
    Currency,
    Page,
    WaitPage,
    models,
)

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = "contest"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    ENDOWMENT = Currency(10)
    PRIZE = Currency(10)
    COST_PER_TICKET = Currency(1)


class Subsession(BaseSubsession):
    def setup_round(self) -> None:
        for group in self.get_groups():
            group.setup_round()

    def determine_outcomes(self) -> None:
        for group in self.get_groups():
            group.determine_outcome()


class Group(BaseGroup):
    prize = models.CurrencyField()

    def setup_round(self) -> None:
        self.prize = C.PRIZE
        for player in self.get_players():
            player.setup_round()

    def determine_outcome(self) -> None:
        total = sum(player.tickets_purchased for player in self.get_players())
        for player in self.get_players():
            player.prize_won = player.tickets_purchased / total
            player.earnings = (
                player.endowment + player.prize_won * self.prize -
                player.cost_per_ticket * player.tickets_purchased
            )


class Player(BasePlayer):
    endowment = models.CurrencyField()
    cost_per_ticket = models.CurrencyField()
    tickets_purchased = models.IntegerField()
    prize_won = models.FloatField()
    earnings = models.CurrencyField()

    @property
    def coplayer(self) -> "Player":
        return self.group.get_player_by_id(3 - self.id_in_group)

    def setup_round(self) -> None:
        self.endowment = C.ENDOWMENT
        self.cost_per_ticket = C.COST_PER_TICKET


# PAGES
class Intro(Page):
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1


class SetupRound(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession: Subsession) -> None:
        subsession.setup_round()


class Decision(Page):
    form_model = "player"
    form_fields = ["tickets_purchased"]

    @staticmethod
    def error_message(player: Player, values: dict) -> str | None:
        if values["tickets_purchased"] < 0:
            return "You cannot buy a negative number of tickets."
        if values["tickets_purchased"] > player.endowment // player.cost_per_ticket:
            return (
                f"Buying {values['tickets_purchased']} tickets would cost "
                f"{values['tickets_purchased'] * player.cost_per_ticket}, "
                f"which is more than your endowment of {player.endowment}."
            )
        return None


class WaitForDecisions(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession: Subsession) -> None:
        subsession.determine_outcomes()


class Results(Page):
    pass


class EndBlock(Page):
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == C.NUM_ROUNDS


page_sequence = [
    Intro,
    SetupRound,
    Decision,
    WaitForDecisions,
    Results,
    EndBlock,
]
