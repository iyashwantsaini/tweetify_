import twint
import pandas as pd
import numpy as np

c = twint.Config()

import twint

# Configure
c = twint.Config()
c.Username = "realDonaldTrump"
c.Search = "great"

# Run
twint.run.Search(c)