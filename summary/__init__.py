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
    NAME_IN_URL = "summary"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    def collect_results(self) -> None:
        for player in self.get_players():
            player.collect_results()


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    payoff_contest = models.CurrencyField()
    payoff_encryption = models.CurrencyField()

    def collect_results(self) -> None:
        self.payoff_contest = Currency(1)
        self.payoff_encryption = Currency(2)


# PAGES
class CollectResults(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession: Subsession) -> None:
        subsession.collect_results()


class Results(Page):
    pass


page_sequence = [
    CollectResults,
    Results,
]
