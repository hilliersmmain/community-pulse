import random

import numpy as np
import pytest
from faker import Faker


@pytest.fixture(autouse=True)
def seed_randomness():
    """Seed all random sources before each test for deterministic results."""
    random.seed(0)
    np.random.seed(0)
    Faker.seed(0)
