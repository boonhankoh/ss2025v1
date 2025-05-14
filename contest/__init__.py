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


class Group(BaseGroup):
    prize = models.CurrencyField()

    def setup_round(self) -> None:
        self.prize = C.PRIZE
        for player in self.get_players():
            player.setup_round()


class Player(BasePlayer):
    endowment = models.CurrencyField()
    cost_per_ticket = models.CurrencyField()
    tickets_purchased = models.IntegerField()

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


class WaitForDecisions(WaitPage):
    wait_for_all_groups = True


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
