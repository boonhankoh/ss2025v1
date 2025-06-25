import random

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
    NUM_ROUNDS = 3


class Subsession(BaseSubsession):
    is_paid = models.BooleanField(initial=False)
    csf = models.StringField(choices=["share", "allpay", "lottery"])

    def setup_round(self) -> None:
        if self.round_number == 1:
            self.setup_paid_rounds()
        self.csf = self.session.config["csf"]
        if self.session.config.get("random_regrouping", False):
            self.group_randomly()
        for group in self.get_groups():
            group.setup_round()

    def setup_paid_rounds(self) -> None:
        for rd in random.choices(self.in_rounds(1, C.NUM_ROUNDS),
                                 k=self.session.config["num_paid_rounds"]):
            rd.is_paid = True

    def determine_outcomes(self) -> None:
        for group in self.get_groups():
            group.determine_outcome()


class Group(BaseGroup):
    prize = models.CurrencyField()

    def setup_round(self) -> None:
        self.prize = self.session.config["prize"]
        for player in self.get_players():
            player.setup_round()

    def determine_outcome_share(self) -> None:
        total = sum(player.tickets_purchased for player in self.get_players())
        for player in self.get_players():
            player.prize_won = player.tickets_purchased / total

    def determine_outcome_lottery(self) -> None:
        try:
            winner = random.choices(self.get_players(),
                                    weights=[p.tickets_purchased for p in self.get_players()])[0]
        except ValueError:
            winner = random.choice(self.get_players())
        for player in self.get_players():
            player.prize_won = 1 if player == winner else 0

    def determine_outcome_allpay(self) -> None:
        max_tickets = max(player.tickets_purchased for player in self.get_players())
        num_tied = len([player for player in self.get_players()
                        if player.tickets_purchased == max_tickets])
        for player in self.get_players():
            if player.tickets_purchased == max_tickets:
                player.prize_won = 1 / num_tied
            else:
                player.prize_won = 0

    def determine_outcome(self) -> None:
        if self.subsession.csf == "share":
            self.determine_outcome_share()
        elif self.subsession.csf == "allpay":
            self.determine_outcome_allpay()
        elif self.subsession.csf == "lottery":
            self.determine_outcome_lottery()
        for player in self.get_players():
            player.earnings = (
                player.endowment + player.prize_won * self.prize -
                player.cost_per_ticket * player.tickets_purchased
            )
            if self.subsession.is_paid:
                player.payoff = player.earnings


class Player(BasePlayer):
    endowment = models.CurrencyField()
    cost_per_ticket = models.CurrencyField()
    tickets_purchased = models.IntegerField()
    prize_won = models.FloatField()
    earnings = models.CurrencyField()

    @property
    def coplayer(self) -> "Player":
        return self.group.get_player_by_id(3 - self.id_in_group)

    @property
    def paid_rounds(self) -> list["Player"]:
        return [r for r in self.in_all_rounds() if r.subsession.is_paid]

    @property
    def total_earnings(self) -> Currency:
        return sum(r.earnings for r in self.paid_rounds)

    def setup_round(self) -> None:
        self.endowment = self.session.config["endowment"]
        self.cost_per_ticket = self.session.config["cost_per_ticket"]

    def record_payoff(self) -> None:
        self.participant.vars["payoff_contest"] = sum(p.earnings for p in self.paid_rounds)


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

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool) -> None:
        player.record_payoff()


page_sequence = [
    Intro,
    SetupRound,
    Decision,
    WaitForDecisions,
    Results,
    EndBlock,
]
