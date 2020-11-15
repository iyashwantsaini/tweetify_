import pandas as pd
from io import StringIO

df = pd.DataFrame(columns=["really long name that goes on for a while", "another really long string", "c"]*6, 
                  data=[["some really long data",2,3]*6,[4,5,6]*6,[7,8,9]*6])
s = StringIO()
df.to_csv(s)
# To get the string use, `s.getvalue()`
# Warning: will exhaust `s`
pd.read_csv(StringIO(s.getvalue()))