import random
import string

from otree.api import (
    BaseConstants,
    BaseGroup,
    BasePlayer,
    BaseSubsession,
    Currency,
    Page,
    models,
)

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = "encryption"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 2
    PAYMENT_PER_CORRECT = Currency(0.10)
    LOOKUP_TABLES = [
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    ]


class Subsession(BaseSubsession):
    payment_per_correct = models.CurrencyField()
    random_seed = models.IntegerField()

    def setup_round(self) -> None:
        self.payment_per_correct = C.PAYMENT_PER_CORRECT
        word = "".join(random.choices(string.ascii_uppercase, k=5))
        for player in self.get_players():
            player.word = word
            player.lookup_table = C.LOOKUP_TABLES[0]


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    time_for_task = models.IntegerField()
    started_task_at = models.FloatField()
    lookup_table = models.StringField()
    word = models.StringField()
    response_1 = models.IntegerField()
    response_2 = models.IntegerField()
    response_3 = models.IntegerField()
    response_4 = models.IntegerField()
    response_5 = models.IntegerField()
    is_correct = models.BooleanField()


def creating_session(subsession: Subsession) -> None:
    subsession.setup_round()


# PAGES
class Intro(Page):
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1


class Decision(Page):
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return True


class Results(Page):
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == C.NUM_ROUNDS


page_sequence = [
    Intro,
    Decision,
    Results,
]
