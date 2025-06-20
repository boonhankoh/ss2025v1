import random
import string
import time

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
    TIME_FOR_TASK = 20


class Subsession(BaseSubsession):
    payment_per_correct = models.CurrencyField()
    random_seed = models.IntegerField()

    def setup_round(self) -> None:
        if self.round_number == 1 and "encryption_random_seed" in self.session.config:
            self.random_seed = self.session.config["encryption_random_seed"]
            random.seed(self.random_seed)
        self.payment_per_correct = C.PAYMENT_PER_CORRECT
        try:
            lookup_table = random.choice(self.session.config["lookup_tables"])
        except KeyError:
            # If lookup tables are not provided, generate permutation randomly
            lookup_table = "".join(random.sample(string.ascii_uppercase, 26))
        word = "".join(random.choices(string.ascii_uppercase, k=5))
        for player in self.get_players():
            player.word = word
            player.lookup_table = lookup_table


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

    def start_task(self) -> None:
        self.time_for_task = self.session.config.get("time_for_encryption_task", C.TIME_FOR_TASK)
        self.started_task_at = time.time()

    def get_remaining_time(self) -> int:
        return self.in_round(1).time_for_task - (time.time() - self.in_round(1).started_task_at)

    @property
    def response_fields(self) -> list[str]:
        return ["response_1", "response_2", "response_3", "response_4", "response_5"]

    @property
    def response_as_list(self) -> list[int]:
        return [self.response_1, self.response_2, self.response_3, self.response_4,
                self.response_5]

    @property
    def lookup_dictionary(self) -> dict[str, int]:
        lookup = {}
        for (index, letter) in enumerate(self.lookup_table):
            lookup[letter] = index
        return lookup

    def compute_outcome(self, timeout_happened: bool) -> None:
        if timeout_happened:
            for response in self.response_fields:
                setattr(self, response, None)
            self.is_correct = False
        else:
            self.is_correct = all(
                response == self.lookup_dictionary[letter]
                for (response, letter) in zip(self.response_as_list, self.word, strict=True)
            )
        if self.is_correct:
            self.payoff = self.subsession.payment_per_correct


def creating_session(subsession: Subsession) -> None:
    subsession.setup_round()


# PAGES
class Intro(Page):
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == 1

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool) -> None:
        player.start_task()


class Decision(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player) -> list[str]:
        return player.response_fields

    @staticmethod
    def get_timeout_seconds(player: Player) -> int:
        return player.get_remaining_time()

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool) -> None:
        player.compute_outcome(timeout_happened)


class Results(Page):
    @staticmethod
    def is_displayed(player: Player) -> bool:
        return player.round_number == C.NUM_ROUNDS


page_sequence = [
    Intro,
    Decision,
    Results,
]
