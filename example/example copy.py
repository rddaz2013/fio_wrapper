import sys
sys.path.insert(0, "/root/src/game/fio_wrapper")

from fio_wrapper import FIO
import pandas as pd
from fastapi.encoders import jsonable_encoder

#fio = FIO(api_key="55a39a35-a65f-4713-bc92-0e2ae344a177")
fio = FIO(api_key="25b273f1-8072-40cd-8e0d-b0afeecf0a41")
#data = pd.read_csv('/root/src/game/fio_wrapper/example/Building_Materials.csv')

material = fio.Exchange.all()
data1 = pd.DataFrame(jsonable_encoder(material))
newdf = data1[(data1.ExchangeCode == "NC1")]

#ds= data.merge(newdf, left_on='Material', right_on='MaterialTicker')
#ds = ds.drop(columns=['AskCount','MaterialTicker','MMBuy','Ask','Bid','BidCount','Demand','MMSell'])
#ds['Value']=ds['Amount']*ds['PriceAverage']
