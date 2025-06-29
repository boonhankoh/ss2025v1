from os import environ

SESSION_CONFIGS = [
    dict(
        name="allpay",
        app_sequence=[
            "contest",
        ],
        csf="allpay",
        endowment=10,
        prize=10,
        cost_per_ticket=1,
        num_demo_participants=2,
    ),
    dict(
        name="share",
        app_sequence=[
            "contest",
        ],
        csf="share",
        endowment=10,
        prize=10,
        cost_per_ticket=1,
        num_demo_participants=2,
    ),
    dict(
        name="lottery",
        app_sequence=[
            "contest",
        ],
        csf="lottery",
        endowment=10,
        prize=10,
        cost_per_ticket=1,
        num_demo_participants=2,
    ),
    dict(
        name="encryption",
        app_sequence=[
            "encryption",
        ],
        encryption_random_seed=12345,
        lookup_tables=[
            "ZYXJIUTLKQSRNWVHGFEDMOPCBA",
            "ZYXWVUTSRQPONMLKJIHGFEDCBA",
            "BADCFEHGJILKNMPORQTSVUXWZY",
        ],
        num_demo_participants=2,
    ),
    dict(
        name="summary_test",
        app_sequence=[
            "contest",
            "encryption",
            "summary",
        ],
        csf="share",
        endowment=10,
        prize=10,
        cost_per_ticket=1,
        num_demo_participants=2,
    ),
    dict(
        name="splash_demo",
        app_sequence=["splash"],
        num_demo_participants=3,
    ),
    dict(
        name="quiz_demo",
        app_sequence=["quiz"],
        num_demo_participants=3,
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=5.00,
    doc="",
    num_paid_rounds=2,
    random_regrouping=True,
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = "en"

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = "GBP"
USE_POINTS = False

ADMIN_USERNAME = "admin"
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = "8668690891855"
